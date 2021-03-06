from spineproxy import SpineProxy
from datetime import datetime, timedelta
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

    def getMedicationPerSlot(self, timeslot):
        for slot in self.timeSlots:
            if slot['name'] == timeslot:
                return slot['medications']
        return None

    def _toDateTime(self,stringValue):
        return datetime.strptime(stringValue, "%Y%m%d%H%M%S")

    def getNextFullDoseTime(self):
        minNextDosageTime = None
        for slot in self.timeSlots:
            for medication in slot['medications']:
                if medication['taken']:
                    nextDosageTime = self._toDateTime(medication['taken']) + timedelta(hours=medication['timeBetweenDosages'])
                    if not minNextDosageTime or nextDosageTime > minNextDosageTime:
                        minNextDosageTime = nextDosageTime

        return minNextDosageTime

    def hasFullDosesLeft(self):
        hasDosesLeft = False
        for slot in self.timeSlots:
            slotNotTaken = True if slot['medications'] else False
            for medication in slot['medications']:
                if medication['taken']:
                    slotNotTaken = False
                    break
            if slotNotTaken:
                return True
        return False

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
                        medication['timeBetweenDosages'] = updatedData['timeBetweenDosages']
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
        dosagePerSlot = prescription[SpineProxy.DOSAGE_KEY]
        doseSlots = prescription[SpineProxy.SLOTS_KEY]
        for slot in timeSlots:
            if slot['name'] in doseSlots and dosagePerSlot > 0:
                slot['medications'].append({
                    'name' : prescription[SpineProxy.NAME_KEY],
                    'dose' : dosagePerSlot,
                    'timeBetweenDosages' : prescription['timeBetweenDosages'],
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
            cls.LATE_AM,
            cls.EARLY_PM,
            cls.LATE_PM,
            cls.EARLY_AM,
            cls.OTHER
        ]

    EARLY_AM = "night"
    LATE_AM = "morning"
    EARLY_PM = "afternoon"
    LATE_PM = "evening"
    OTHER = "other"
