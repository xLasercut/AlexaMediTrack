from flask import render_template
from importdata.prescriptions import DailyDosage

class UserDataReader(object):

    def getNextFullDoseTime(self, userData):
        earliestDoseTime = userData.getNextFullDoseTime()
        if userData.hasFullDosesLeft():
            if earliestDoseTime:
                return "You can take your next dose at {} ".format(earliestDoseTime.strftime("%H %M"))
            else:
                return "You have not taken any doses today yet. "
        else:
            return "You have taken all your doses for today. "

    def getDoseString(self, dose):
        if dose > 1:
            return "doses"
        else:
            return "dose"

    def getSlotString(self, slot):
        if slot == "night":
            return "tonight"
        elif slot == "other":
            return "your other medication"
        else:
            return "this {}".format(slot)

    def readCurrentStatus(self, userData):
        medInfo = []
        medTaken = userData.getAllMedicationTaken()
        medNotTaken = userData.getAllMedicationNotTaken()

        print medTaken
        print medNotTaken

        if not medTaken and medNotTaken:
            for slot in medNotTaken:
                medInfoString = render_template('status_yet_to_take', timeslot=self.getSlotString(slot["name"]))
                medInfo.append(medInfoString)
                for medication in slot["medications"]:
                    doseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
        elif not medNotTaken and medTaken:
            for slot in medTaken:
                medInfoString = render_template('status_taken', timeslot=self.getSlotString(slot["name"]))
                medInfo.append(medInfoString)
                for medication in slot["medications"]:
                    doseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
        elif medTaken and medNotTaken:
            for slot in medTaken:
                medInfoString = render_template('status_taken', timeslot=self.getSlotString(slot["name"]))
                medInfo.append(medInfoString)
                for medication in slot["medications"]:
                    doseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
            for slot in medNotTaken:
                for medication in slot["medications"]:
                    doseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
        else:
            return render_template('status_empty_list')

        return "".join(medInfo)

class AlexaInputSanitizer(object):

    SANITIZE_DATA = [
        {
            "synonyms": ["Night"],
            "actualValue": "night"
        },
        {
            "synonyms": ["Afternoon"],
            "actualValue": "afternoon"
        },
        {
            "synonyms": ["Morning"],
            "actualValue": "morning"
        },
        {
            "synonyms": ["Evening"],
            "actualValue": "evening"
        },
        {
            "synonyms": ["others"],
            "actualValue": "other"
        }
    ]

    def sanitizeInputs(self, inputString):
        for item in self.SANITIZE_DATA:
            if inputString.strip() in item["synonyms"]:
                return item["actualValue"]
        return inputString.lower().strip()
