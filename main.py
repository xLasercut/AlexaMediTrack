#!/usr/bin/env python


from flask import Flask, render_template, jsonify
from flask_ask import Ask, statement, question, session, convert_errors
from afg import Supervisor

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

@ask.intent('AMAZON.HelpIntent')
def help_user():
    context_help = sup.get_help()
    # context_help string could be extended with some dynamic information
    return question(context_help)

@ask.launch
@sup.guide
def launched():
    return question(render_template("welcome"))

@ask.intent("MedicationInfo")
@sup.guide
def choose_medication_info():
    close_user_session()
    return statement("this is your medication information")

@ask.intent("SetupTracker")
@sup.guide
def choose_setup_tracker():
    tracker_input()
    return question(render_template("tracker_setup_welcome"))

@sup.guide
def tracker_input():
    print("end of scenario")


if __name__ == '__main__':
    app.run(debug=True)
