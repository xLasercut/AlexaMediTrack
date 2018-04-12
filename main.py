#!/usr/bin/env python


from flask import Flask, render_template, jsonify
from flask_ask import Ask, statement, question, session, convert_errors, context
import json
import logging
import os.path
import datetime

from datasource import UserDataSource, UserIdMapping
from importdata.prescriptions import PrescriptionFinder, DailyDosage
from importdata.spineproxy import FakeSpineProxy
from alexareader import UserDataReader

#logging.getLogger("flask_ask").setLevel(logging.DEBUG)

app = Flask(__name__)
ask = Ask(app, '/')

USER_DATA_PATH = "user_data.json"

EARLY_AM_SLOT = "Early AM"
EARLY_PM_SLOT = "Early PM"
LATE_AM_SLOT = "Late AM"
LATE_PM_SLOT = "Late AM"

@ask.on_session_started
def newSession():
    app.logger.debug('new user session started')


def closeUserSession():
    app.logger.debug("user session stopped")


@ask.session_ended
def sessionEnded():
    closeUserSession()
    return "", 200

def sanitizeInputs(inputString):
    return inputString.lower()

def getUserData(userId):
    source = UserDataSource()
    data = source.load(userId)
    if data:
        return DailyDosage(data, source)
    else:
        return PrescriptionFinder(FakeSpineProxy(), source).getPrescriptions(userId)

def determineTimeSlot(datetime):
    if datetime.hour in range(0,6):
        return EARLY_AM_SLOT
    elif datetime.hour in range(6,12):
        return LATE_AM_SLOT
    elif datetime.hour in range(12,18):
        return EARLY_PM_SLOT
    elif datetime.hour in range(18,24):
        return LATE_PM_SLOT
    return "Other"

def writeUserData(userData):
    """
    Write user data to disk
    """
    try:
        userData.updateState()
    except:
        closeUserSession()
        print "error saving user data"

@ask.launch
def launched():
    return question(render_template("welcome"))

@ask.intent("medTakenInfo")
def medicationTakenInfo():
    """
    Returns the amount of medication taken
    """
    userId = context.System.device.deviceId
    alexaReader = UserDataReader()

    userData = getUserData(userId)
    return statement(alexaReader.readCurrentStatus(userData))

@ask.intent("addMedToPlan", convert={"dose": int, "medicationName": "MedicationNameSlot", "timeSlot": "MedTimeSlot"})
def addMedToPlan(medicationName, dose, timeSlot):
    """
    Add medication to list
    - if medication already exist on list, then increase the total amount
    """
    if medicationName is None or dose is None or timeSlot is None:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        timeSlot = sanitizeInputs(timeSlot)
        medicationName = sanitizeInputs(medicationName)
        for slot in userData.timeSlots:
            if slot["name"] == timeSlot:
                match = False
                for medication in slot["medications"]:
                    if medication["name"] == medicationName:
                        medication["dose"] += dose
                        match = True
                        break
                if match == False:
                    medData = {
                        "name": medicationName,
                        "taken": "None",
                        "dose": dose
                    }
                    slot["medications"].append(medData)
                writeUserData(userData)
                break
        return statement("Added %i dose of %s to %s" %(dose, medicationName, timeSlot))

@ask.intent("removeMedFromPlan", convert={"medicationName": "MedicationNameSlot", "timeSlot": "MedTimeSlot"})
def removeMedFromPlan(medicationName, timeSlot):
    """
    Deletes medication from both 'planned' and 'actual' lists
    """
    if medicationName is None or timeSlot is None:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        timeSlot = sanitizeInputs(timeSlot)
        medicationName = sanitizeInputs(medicationName)
        for slot in userData.timeSlots:
            if slot["name"] == timeSlot:
                match = False
                for i in range(0, len(slot["medications"])):
                    if slot["medications"][i]["name"] == medicationName:
                        del slot["medications"][i]
                        match = True
                        writeUserData(userData)
                        break
                if match == False:
                    return statement("could not find %s in %s slot" %(medicationName, timeSlot))
                else:
                    return statement("removed %s from %s slot" %(medicationName, timeSlot))

@ask.intent("listMedFromPlan")
def listMedFromPlan():
    """
    Returns the amount and type of medication from the 'planned' list
    """
    userId = context.System.device.deviceId
    userData = getUserData(userId)
    medList = []
    for slot in userData.timeSlots:
        if len(slot["medications"]) > 0:
            medList.append("%s slot contains:" %(slot["name"]))
        for medication in slot["medications"]:
            medList.append("%i dose of %s" %(medication["dose"], medication["name"]))

    if len(medList) > 0:
        return statement("Your medications list: %s" %(" ".join(medList)))
    else:
        return statement("Your medications list is empty")


@ask.intent("recordMedication")
def recordmeds(MedicationName):
    timestamp = datetime.datetime.now()
    takenTime = str(timestamp.strftime("%I:%M %p"))
    timestampString = str(timestamp.strftime("%Y%m%d%H%M%S"))
    print MedicationName
    if MedicationName is None:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(USER_DATA_PATH, userId)
        medicationName = sanitizeInputs(MedicationName)
        timeSlot = determineTimeSlot(timestamp)
        for slot in userData["timeSlots"]:
            if slot["name"] == timeSlot:
                match = False
                for medication in slot["medications"]:
                    if medication["name"] == medicationName:
                        medication["taken"] = timestampString
                        medication["dose"] += 1
                        match = True
                        break
                if match == False:
                    medData = {
                        "taken": timestampString,
                        "name": medicationName,
                        "dose": 1
                    }
                    slot["medications"].append(medData)
                writeUserData(USER_DATA_PATH, userData)
                break
        return statement("I've recorded that you took " + medicationName + " at "+ takenTime )

if __name__ == '__main__':
    app.run(debug=True)
