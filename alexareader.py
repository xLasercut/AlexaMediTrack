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

    def readCurrentStatus(self, userData):
        medInfo = []
        medTaken = userData.getAllMedicationTaken()
        medNotTaken = userData.getAllMedicationNotTaken()

        print medTaken
        print medNotTaken

        if not medTaken:
            for slot in medNotTaken:
                medInfo.append("You have yet to take {} dose, containing:".format(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("{} {} of {}.".format(medication["dose"], self.getDoseString(medication["dose"]), medication["name"]))
        elif not medNotTaken:
            for slot in medTaken:
                medInfo.append("You have taken {} dose, containing:".format(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("{} {} of {}.".format(medication["dose"], self.getDoseString(medication["dose"]), medication["name"]))
        elif medTaken and medNotTaken:
            for slot in medTaken:
                medInfo.append("For {} dose, you have taken:".format(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("{} {} of {}.".format(medication["dose"], self.getDoseString(medication["dose"]), medication["name"]))
            for slot in medNotTaken:
                medInfo.append("For {} dose, you have yet to take:".format(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("{} {} of {}.".format(medication["dose"], self.getDoseString(medication["dose"]), medication["name"]))
        else:
            return "Your medication list is empty"

        return " ".join(medInfo)

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
