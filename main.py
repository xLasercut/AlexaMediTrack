#!/usr/bin/env python


from flask import Flask, render_template, jsonify
from flask_ask import Ask, statement, question, session, convert_errors
from afg import Supervisor
import json

app = Flask("MedTracker")
ask = Ask(app, '/')
sup = Supervisor("scenario.yaml")




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
        return statement("error retrieving user data")


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
    medication_taken = ""
    med_data = get_user_data("user_data.json")
    for medicine_taken, amount_taken in med_data[0]["medications"]["actual"].iteritems():
        for medicine_planned, amount_planned in med_data[0]["medications"]["planned"].iteritems():
            if medicine_planned == medicine_taken:
                medication_taken += "%i out of %i for %s. " %(amount_taken, amount_planned, medicine_taken)
                break

    output_msg = "You have taken: %s" %(medication_taken)

    close_user_session()
    return statement(output_msg)


if __name__ == '__main__':
    app.run(debug=True)
