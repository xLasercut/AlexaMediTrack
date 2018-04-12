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

    def getMedication(self, timeslot, name):
        for slot in self.timeSlots:
            if slot['name'] == timeslot:
                for medication in slot['medications']:
                    if medication['name'] == name:
                        return medication
                return None

    def updateMedication(self, timeslot, name, updatedData):
        for slot in self.timeSlots:
            if slot['name'] == timeslot:
                match = False
                for medication in slot['medications']:
                    if medication['name'] == name:
                        medication['name'] = updatedData['name']
                        medication['taken'] = updatedData['taken']
                        medication['dose'] = updatedData['dose']
                        match = True
                        break
                if not match:
                    slot['medications'].append(updatedData)
                self.updateState()
                break

    def removeMedication(self, timeslot, name):
        for slot in self.timeSlots:
            if slot['name'] == timeslot:
                for i in range(0, len(slot["medications"])):
                    if slot["medications"][i]["name"] == name:
                        del slot["medications"][i]
                        self.updateState()
                        break
                break

    def getAllMedicationTaken(self):
        dosagesTaken = []
        for slot in self.timeSlots:
            takenSlot = {
                'name' : slot['name'],
                'medications' :[]
            }
            for medication in slot['medications']:
                if medication['taken']:
                    takenSlot['medications'].append(medication)

            if takenSlot['medications']:
                dosagesTaken.append(takenSlot)

        return dosagesTaken

    def getAllMedicationNotTaken(self):
        dosagesTaken = []
        for slot in self.timeSlots:
            notTakenSlot = {
                'name' : slot['name'],
                'medications' :[]
            }
            for medication in slot['medications']:
                if not medication['taken']:
                    notTakenSlot['medications'].append(medication)

            if notTakenSlot['medications']:
                dosagesTaken.append(notTakenSlot)

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
        print distibution
        for i, dosage in enumerate(distibution):
            if dosage > 0:
                timeSlots[i]['medications'].append({
                    'name' : prescription[SpineProxy.NAME_KEY],
                    'dose' : dosage,
                    'taken': None
                })

    def _getTimeSlots(self):
        slotNames = TimeSlices.getFourSlots()

        slots = []
        for slotName in slotNames:
            slot = {}
            slot['name'] = slotName
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

    EARLY_AM = "early AM"
    LATE_AM = "late AM"
    EARLY_PM = "early PM"
    LATE_PM = "late PM"
    OTHER = "other"
