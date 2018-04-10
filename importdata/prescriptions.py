from spineproxy import SpineProxy
from datetime import datetime

class DailyDosage(object):
    def __init__(self, initialSource, user, userDataSource):
        self.state = initialSource
        self.user = user
        self.userDataSource = userDataSource

    @property
    def timeSlots(self):
        return self.state['timeSlots']

    def takeMedication(self, timeslot):
        for slot in self.timeSlots:
            if slot['name'] == timeslot and not slot['taken']:
                slot['taken'] = datetime.now().strftime("%Y%M%D-%H%M%S")
                break

        self._updateState()

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

    def _updateState(self):
        self.userDataSource.saveUserState(self.user, self.state)

class PrescriptionFinder(object):
    def __init__(self, spineProxy, userDataSource):
        self.spineProxy = spineProxy
        self.userDataSource = userDataSource

    def getPrescriptionsByNhsNumber(self, nhsNumber):
        prescriptions = self.getPrescriptions(nhsNumber)
        return DailyDosage(self._createDailyDosage(prescriptions), nhsNumber, self.userDataSource)

    def _createDailyDosage(self, sourcePrescriptions):

        dailyDosagePlan = {}
        timeSlots = self._getTimeSlots()
        for prescription in sourcePrescriptions[SpineProxy.MEDICATION_KEY]:
            self._addDosage(prescription, timeSlots)

        dailyDosagePlan['date'] = datetime.now().strftime("%Y%M%D")
        dailyDosagePlan['timeSlots'] = timeSlots
        return dailyDosagePlan

    def _addDosage(self, prescription, timeSlots):
        dailyDosage = prescription[SpineProxy.DOSAGE_KEY]
        distibution = self._getDistribution(dailyDosage, len(timeSlots))
        for i, dosage in enumerate(distibution):
            timeSlots[i]['medications'].append({
                'name' : prescription[SpineProxy.NAME_KEY],
                'dose' : dosage
            })

    def _getTimeSlots(self):
        slotNames = TimeSlices.getFourSlots()

        slots = []
        for slotName in slotNames:
            slot = {}
            slot['name'] = slotName
            slot['taken'] = None
            slots.append(slot)

        return slots

    def _getDistribution(self, dosage, slots = 4):
        """ simple and wrong pill distributor TODO make a better one """
        dist = [slots]
        base = dosage / slots
        remainder = dosage % slots

        for slot in range(slots):
            dist[slot] = base
            if slot <= remainder:
                dist[slot] += 1

        return dist

class TimeSlices(object):

    @staticmethod
    def getFourSlots(self):
        return [
            self.EARLY_AM,
            self.LATE_AM,
            self.EARLY_PM,
            self.LATE_PM
        ]

    EARLY_AM = "EarlyAM"
    LATE_AM = "LateAM"
    EARLY_PM = "EarlyPM"
    LATE_PM = "LatePM"
