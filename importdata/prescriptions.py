from spineproxy import SpineProxy
from datetime import datetime
from datasource import UserIdMapping

class DailyDosage(object):
    def __init__(self, initialSource, userDataSource):
        self.state = initialSource
        self.userDataSource = userDataSource

    @property
    def date(self):
        return self.state['date']

    @property
    def timeSlots(self):
        return self.state['timeSlots']

    @property
    def userId(self):
        return self.state['userId']

    def takeMedication(self, timeslot):
        for slot in self.timeSlots:
            if slot['name'] == timeslot:
                for medication in slot["medications"]:
                    medication['taken'] = datetime.now().strftime("%Y%m%d-%H%M%S")
                break

        self.updateState()

    def hasTaken(self, timeslot):
        for slot in self.timeSlots:
            if slot['name'] == timeslot and slot['taken']:
                return True

        return False

    def getTotalTaken(self):
        dosagesTaken = []
        for slot in self.timeSlots:
            if slot['taken']:
                dosagesTaken.append(slot)

        return dosagesTaken

    def updateState(self):
        self.userDataSource.save(self.userId, self.state)

class PrescriptionFinder(object):
    def __init__(self, spineProxy, userDataSource):
        self.spineProxy = spineProxy
        self.userDataSource = userDataSource

    def getPrescriptions(self, userId):
        nhsNumber = UserIdMapping().getNhsNumberFromUserId(userId)
        prescriptions = self.spineProxy.getPrescriptions(nhsNumber)
        dailyDosageDict = self._createDailyDosage(prescriptions)
        dailyDosageDict['userId'] = userId
        return DailyDosage(dailyDosageDict, self.userDataSource)

    def _createDailyDosage(self, sourcePrescriptions):

        dailyDosagePlan = {}
        timeSlots = self._getTimeSlots()
        for prescription in sourcePrescriptions[SpineProxy.MEDICATION_KEY]:
            self._addDosage(prescription, timeSlots)

        dailyDosagePlan['date'] = datetime.now().strftime("%Y%m%d")
        dailyDosagePlan['timeSlots'] = timeSlots
        return dailyDosagePlan

    def _addDosage(self, prescription, timeSlots):
        dailyDosage = prescription[SpineProxy.DOSAGE_KEY]
        distibution = self._getDistribution(dailyDosage, len(timeSlots))
        for i, dosage in enumerate(distibution):
            timeSlots[i]['medications'].append({
                'name' : prescription[SpineProxy.NAME_KEY],
                'taken': None,
                'dose' : dosage
            })

    def _getTimeSlots(self):
        slotNames = TimeSlices.getFourSlots()

        slots = []
        for slotName in slotNames:
            slot = {}
            slot['name'] = slotName
            slot['taken'] = None
            slot['medications'] = []
            slots.append(slot)

        return slots

    def _getDistribution(self, dosage, slots = 4):
        """ simple and wrong pill distributor TODO make a better one """
        dist = []
        base = dosage / slots
        remainder = dosage % slots

        for slot in range(slots):
            dist.append(base)
            if slot <= remainder:
                dist[slot] += 1

        return dist

class TimeSlices(object):

    @classmethod
    def getFourSlots(cls):
        return [
            cls.EARLY_AM,
            cls.LATE_AM,
            cls.EARLY_PM,
            cls.LATE_PM,
            cls.OTHER
        ]

    EARLY_AM = "early am"
    LATE_AM = "late am"
    EARLY_PM = "early pm"
    LATE_PM = "late pm"
    OTHER = "other"
