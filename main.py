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
from alexareader import UserDataReader, AlexaInputSanitizer

#logging.getLogger("flask_ask").setLevel(logging.DEBUG)

app = Flask(__name__)
ask = Ask(app, '/')

USER_DATA_PATH = "user_data.json"

EARLY_AM_SLOT = "night"
EARLY_PM_SLOT = "afternoon"
LATE_AM_SLOT = "morning"
LATE_PM_SLOT = "evening"

@ask.on_session_started
def newSession():
    app.logger.debug('new user session started')


def closeUserSession():
    app.logger.debug("user session stopped")


@ask.session_ended
def sessionEnded():
    closeUserSession()
    return "", 200

def getDoseString(dose):
    if dose > 1:
        return "doses"
    else:
        return "dose"

def getUserData(userId):
    source = UserDataSource()
    data = source.load(userId)
    if data:
        return DailyDosage(data, source)
    else:
        return PrescriptionFinder(FakeSpineProxy(), source).getPrescriptions(userId)

def determineTimeSlot(datetime):
    if datetime.hour in range(0,4):
        return EARLY_AM_SLOT
    elif datetime.hour in range(4,12):
        return LATE_AM_SLOT
    elif datetime.hour in range(12,18):
        return EARLY_PM_SLOT
    elif datetime.hour in range(18,24):
        return LATE_PM_SLOT
    return "other"

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

@ask.intent("nextSlotToTake")
def medicationTakenInfo():
    """
    Returns the next time that a slot full of medication can be taken
    """
    userId = context.System.device.deviceId
    alexaReader = UserDataReader()
    userData = getUserData(userId)

    return statement(alexaReader.getNextFullDoseTime(userData))

@ask.intent("medTakenInfo")
def medicationTakenInfo():
    """
    Returns the amount of medication taken
    """
    userId = context.System.device.deviceId
    alexaReader = UserDataReader()

    userData = getUserData(userId)
    return statement(alexaReader.readCurrentStatus(userData))

@ask.intent("addMedToPlan", convert={"dose": int, "medicationName": "MedicationNameSlot", "timeSlot": "MedTimeSlot", "timeBetweenDosages" : "TimeBetweenDosages"})
def addMedToPlan(medicationName, dose, timeSlot, timeBetweenDosages):
    """
    Add medication to list
    - if medication already exist on list, then increase the total amount
    """
    if not medicationName or not dose or not timeSlot:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        sanitizer = AlexaInputSanitizer()
        medicationName = sanitizer.sanitizeInputs(medicationName)
        timeBetweenDosages = sanitizer.sanitizeInputs(timeBetweenDosages)
        timeSlot = sanitizer.sanitizeInputs(timeSlot)
        medicationData = userData.getMedication(timeSlot, medicationName)
        if not medicationData:
            medicationData = {
                "name": medicationName,
                "taken": None,
                "dose": dose,
                "timeBetweenDosages" : timeBetweenDosages
            }
        else:
            medicationData['dose'] += dose
        userData.updateMedication(timeSlot, medicationName, medicationData)
        return statement("Added {} {} of {} to {} every {}".format(dose, getDoseString(dose), medicationName, timeSlot, timeBetweenDosages))

@ask.intent("removeMedFromPlan", convert={"medicationName": "MedicationNameSlot", "timeSlot": "MedTimeSlot"})
def removeMedFromPlan(medicationName, timeSlot):
    """
    Deletes medication from both 'planned' and 'actual' lists
    """
    if not medicationName or not timeSlot:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        sanitizer = AlexaInputSanitizer()
        medicationName = sanitizer.sanitizeInputs(medicationName)
        timeSlot = sanitizer.sanitizeInputs(timeSlot)
        userData.removeMedication(timeSlot, medicationName)
        return statement("removed {} from {} slot".format(medicationName, timeSlot))

@ask.intent("recordMedicationByName", convert={"medicationName": "MedicationNameSlot", "timeSlot": "MedTimeSlot"})
def recordmeds(medicationName, timeSlot):
    timestamp = datetime.datetime.now()
    takenTime = str(timestamp.strftime("%I:%M %p"))
    timestampString = str(timestamp.strftime("%Y%m%d%H%M%S"))
    if not medicationName:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        sanitizer = AlexaInputSanitizer()
        medicationName = sanitizer.sanitizeInputs(medicationName)
        if not timeSlot:
            timeSlot = determineTimeSlot(timestamp)
        else:
            timeSlot = sanitizer.sanitizeInputs(timeSlot)
        medicationData = userData.getMedication(timeSlot, medicationName)
        if not medicationData:
            medicationData = {
                "name": medicationName,
                "taken": timestampString,
                "dose": 1
            }
        else:
            medicationData['taken'] = timestampString
        userData.updateMedication(timeSlot, medicationName, medicationData)
        return statement("I've recorded that you took {} for {} slot".format(medicationName, timeSlot))

@ask.intent("recordMedicationByTimeSlot", convert={"timeSlot": "MedTimeSlot"})
def recordMedsTimeSlot(timeSlot):
    if not timeSlot:
        return question(render_template("ask_for_repeat"))
    else:
        timestamp = datetime.datetime.now()
        timestampString = str(timestamp.strftime("%Y%m%d%H%M%S"))
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        sanitizer = AlexaInputSanitizer()
        timeSlot = sanitizer.sanitizeInputs(timeSlot)
        for slot in userData.timeSlots:
            if slot["name"] == timeSlot:
                for medication in slot["medications"]:
                    medication["taken"] = timestampString
                break
        userData.updateState()
        return statement("I've recorded that you took your {} medication.".format(timeSlot))
if __name__ == '__main__':
    app.run(debug=True)
