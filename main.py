#!/usr/bin/env python


from flask import Flask, render_template, jsonify
from flask_ask import Ask, statement, question, session, convert_errors
from afg import Supervisor
import json
import logging

#logging.getLogger("flask_ask").setLevel(logging.DEBUG)

app = Flask("MedTracker")
ask = Ask(app, '/')
sup = Supervisor("scenario.yaml")

USER_DATA_PATH = "user_data.json"


@ask.on_session_started
@sup.start
def new_session():
    app.logger.debug('new user session started')


@sup.stop
def close_user_session():
    app.logger.debug("user session stopped")


@ask.session_ended
def session_ended():
    close_user_session()
    return "", 200

def get_user_data(file_path):
    try:
        with open(file_path) as user_data_file:
            user_data = json.load(user_data_file)
        return user_data
    except:
        close_user_session()
        print "error getting user data"

def write_user_data(file_path, data_to_write):
    try:
        with open(file_path, "w") as user_data_file:
            json.dump(data_to_write, user_data_file)
    except:
        close_user_session()
        print "error saving user data"

@ask.intent('AMAZON.HelpIntent')
def help_user():
    context_help = sup.get_help()
    # context_help string could be extended with some dynamic information
    return question(context_help)


@ask.launch
def launched():
    return question(render_template("welcome"))

@ask.intent("medTakenInfo")
def medication_taken_info():
    med_list = []
    med_data = get_user_data(USER_DATA_PATH)
    for medicine_taken, amount_taken in med_data[0]["medications"]["actual"].iteritems():
        for medicine_planned, amount_planned in med_data[0]["medications"]["planned"].iteritems():
            if medicine_planned == medicine_taken:
                med_list.append("%i out of %i for %s." %(amount_taken, amount_planned, medicine_taken))
                break

    output_msg = "You have taken: %s" %(" ".join(med_list))

    close_user_session()
    return statement(output_msg)

@ask.intent("addMedToPlan", convert={"MedicationAmount":int, "MedicationName":"MedicationNameSlot"})
def add_medication_to_plan(MedicationAmount, MedicationName):
    if MedicationAmount is None or MedicationName is None:
        return question(render_template("ask_for_repeat"))
    else:
        med_data = get_user_data(USER_DATA_PATH)
        if MedicationName not in med_data[0]["medications"]["planned"]:
            med_data[0]["medications"]["planned"][MedicationName] = MedicationAmount
        else:
            med_data[0]["medications"]["planned"][MedicationName] += MedicationAmount

        if MedicationName not in med_data[0]["medications"]["actual"]:
            med_data[0]["medications"]["actual"][MedicationName] = 0

        write_user_data(USER_DATA_PATH, med_data)
        return statement("Added %i of %s to medication plan" %(MedicationAmount, MedicationName))

@ask.intent("removeMedFromPlan", convert={"MedicationName":"MedicationNameSlot"})
def remove_med_from_plan(MedicationName):
    if MedicationName is None:
        return question(render_template("ask_for_repeat"))
    else:
        med_data = get_user_data(USER_DATA_PATH)
        if MedicationName in med_data[0]["medications"]["planned"]:
            del med_data[0]["medications"]["actual"][MedicationName]
            del med_data[0]["medications"]["planned"][MedicationName]

            write_user_data(USER_DATA_PATH, med_data)
            return statement("removed %s from plan" %(MedicationName))
        else:
            return statement("could not find %s in plan" %(MedicationName))

@ask.intent("listMedFromPlan")
def list_med_from_plan():
    med_data = get_user_data(USER_DATA_PATH)
    med_list = []
    for medicine, ammount in med_data[0]["medications"]["planned"].iteritems():
        med_list.append("%i of %s." %(ammount, medicine))
    if len(med_list) > 0:
        return statement("Your medication list: %s" %(" ".join(med_list)))
    else:
        return statement("Your medication list is empty")


if __name__ == '__main__':
    app.run(debug=True)
