from importdata.prescriptions import DailyDosage

class UserDataReader(object):

    def readCurrentStatus(self, userData):
        medInfo = []
        medTaken = userData.getAllMedicationTaken()
        medNotTaken = userData.getAllMedicationNotTaken()

        print medTaken
        print medNotTaken

        if not medTaken:
            for slot in medNotTaken:
                medInfo.append("You have yet to take %s dose, containing:" %(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("%i dose of %s." %(medication["dose"], medication["name"]))
        elif not medNotTaken:
            for slot in medTaken:
                medInfo.append("You have taken %s dose, containing:" %(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("%i dose of %s." %(medication["dose"], medication["name"]))
        elif medTaken and medNotTaken:
            for slot in medTaken:
                medInfo.append("For %s dose, you have taken:" %(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("%i dose of %s." %(medication["dose"], medication["name"]))
            for slot in medNotTaken:
                medInfo.append("For %s dose, you have yet to take:" %(slot["name"]))
                for medication in slot["medications"]:
                    medInfo.append("%i dose of %s." %(medication["dose"], medication["name"]))
        else:
            return "Your medication list is empty"

        return " ".join(medInfo)
