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


@ask.launch
@sup.guide
def launched():
    return question(render_template("welcome"))

@ask.intent("MedTakenInfo")
@sup.guide
def medTakenInfo():
    return statement("this is your medication information")

@ask.intent("SetupReminder")
@sup.guide
def setupReminder():
    return statement("setting up reminder")

@sup.guide
def endEvent():
    return statement("End of scenario")

if __name__ == '__main__':
    app.run(debug=True)
