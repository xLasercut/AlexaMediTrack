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

#logging.getLogger("flask_ask").setLevel(logging.DEBUG)

app = Flask(__name__)
ask = Ask(app, '/')

USER_DATA_PATH = "user_data.json"


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
    medsTaken = []
    userId = context.System.device.deviceId
    userData = getUserData(userId)
    for slot in userData.timeSlots:
        if slot["taken"] != "None" and len(slot["medications"]) > 0:
            medsTaken.append("You have taken your dose for %s, containing:" %(slot["name"]))
        elif slot["taken"] == "None" and len(slot["medications"]) > 0:
            medsTaken.append("You have yet to take your dose for %s, containing:" %(slot["name"]))
        for medication in slot["medications"]:
            medsTaken.append("%i dose of %s." %(medication["dose"], medication["name"]))

    closeUserSession()
    if len(medsTaken) > 0:
        return statement(" ".join(medsTaken))
    else:
        return statement("Your medications list is empty")


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


if __name__ == '__main__':
    app.run(debug=True)
