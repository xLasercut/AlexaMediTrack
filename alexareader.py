from flask import render_template
from importdata.prescriptions import DailyDosage

class UserDataReader(object):

    def getNextFullDoseTime(self, userData):
        earliestDoseTime = userData.getNextFullDoseTime()
        if userData.hasFullDosesLeft():
            if earliestDoseTime:
                return "You can take your next dose at {}".format(earliestDoseTime.strftime("%H %M"))
            else:
                return "You have not taken any doses today yet"
        else:
            return "You have taken all your doses for today"

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

        if not medTaken:
            for slot in medNotTaken:
<<<<<<< HEAD
                medInfoString = render_template('status_yet_to_take', timeslot=getSlotString(slot["name"]))
=======
                medInfoString = render_template('status_yet_to_take', timeslot=self.getSlotString(slot["name"]))
>>>>>>> tim
                medInfo.append(medInfoString)
                for medication in slot["medications"]:
                    doseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
        elif not medNotTaken:
            for slot in medTaken:
                medInfo.append("You have taken {} dose, containing:".format(slot["name"]))
                for medication in slot["medications"]:
                    oseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
        elif medTaken and medNotTaken:
            for slot in medTaken:
                medInfo.append("For {} dose, you have taken:".format(slot["name"]))
                for medication in slot["medications"]:
                    doseString = self.getDoseString(medication["dose"])
                    medInfoString = render_template('status_measurement', dosenumber=medication["dose"], dosestring=doseString, medicationname=medication["name"])
                    medInfo.append(medInfoString)
            for slot in medNotTaken:
                medInfo.append("For {} dose, you have yet to take:".format(slot["name"]))
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
