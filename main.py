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

EARLY_AM_SLOT = "early AM"
EARLY_PM_SLOT = "early PM"
LATE_AM_SLOT = "late AM"
LATE_PM_SLOT = "late PM"

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
    return inputString.lower().strip()

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
    if datetime.hour in range(0,6):
        return EARLY_AM_SLOT
    elif datetime.hour in range(6,12):
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
    if not medicationName or not dose or not timeSlot:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        medicationName = sanitizeInputs(medicationName)
        medicationData = userData.getMedication(timeSlot, medicationName)
        if not medicationData:
            medicationData = {
                "name": medicationName,
                "taken": None,
                "dose": dose
            }
        else:
            medicationData['dose'] += dose
        userData.updateMedication(timeSlot, medicationName, medicationData)
        return statement("Added {} {} of {} to {}".format(dose, getDoseString(dose), medicationName, timeSlot))

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
        medicationName = sanitizeInputs(medicationName)
        userData.removeMedication(timeSlot, medicationName)
        return statement("removed {} from {} slot".format(medicationName, timeSlot))

@ask.intent("listMedFromPlan")
def listMedFromPlan():
    """
    Returns the amount and type of medication from the 'planned' list
    """
    userId = context.System.device.deviceId
    userData = getUserData(userId)
    medList = []
    for slot in userData.timeSlots:
        if slot["medications"]:
            medList.append("{} slot contains:".format(slot["name"]))
        for medication in slot["medications"]:
            medList.append("{} {} of {}".format(medication["dose"], getDoseString(medication["dose"]), medication["name"]))

    if medList:
        return statement("Your medications list: {}".format(" ".join(medList)))
    else:
        return statement("Your medications list is empty")


@ask.intent("recordMedication", convert={"medicationName": "MedicationNameSlot", "timeSlot": "MedTimeSlot"})
def recordmeds(medicationName, timeSlot):
    timestamp = datetime.datetime.now()
    takenTime = str(timestamp.strftime("%I:%M %p"))
    timestampString = str(timestamp.strftime("%Y%m%d%H%M%S"))
    if not medicationName:
        return question(render_template("ask_for_repeat"))
    else:
        userId = context.System.device.deviceId
        userData = getUserData(userId)
        medicationName = sanitizeInputs(medicationName)
        if not timeSlot:
            timeSlot = determineTimeSlot(timestamp)
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

if __name__ == '__main__':
    app.run(debug=True)
