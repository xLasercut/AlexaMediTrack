from importdata.prescriptions import DailyDosage

class UserDataReader(object):

    def readCurrentStatus(self, userData):
        medInfo = []

        for slot in userData.timeSlots:
            if len(slot["medications"]) > 0:
                slotInfo = {
                    "timeSlot": slot["name"],
                    "taken": [],
                    "notTaken": []
                }
                for medication in slot["medications"]:
                    if medication["taken"] != "None":
                        slotInfo["taken"].append("%i of %s." % (medication["dose"], medication["name"]))
                    else:
                        slotInfo["notTaken"].append("%i of %s." % (medication["dose"], medication["name"]))
                medInfo.append(slotInfo)

        if len(medInfo) > 0:
            msgOut = []
            for item in medInfo:
                if len(item["notTaken"]) == 0:
                    msgOut.append(
                        "You have taken your %s dose, containing: %s" % (item["timeSlot"], " ".join(item["taken"])))
                elif len(item["taken"]) == 0:
                    msgOut.append("You have yet to take your %s dose, containing: %s" % (
                    item["timeSlot"], " ".join(item["notTaken"])))
                else:
                    msgOut.append("For your %s dose, you have taken: %s you have yet to take: %s." % (
                    item["timeSlot"], " ".join(item["taken"]), " ".join(item["notTaken"])))
            return " ".join(msgOut)
        else:
            return "Your medications list is empty"
