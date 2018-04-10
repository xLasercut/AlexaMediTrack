from importdata.prescriptions import DailyDosage

class UserDataReader(object):

    def readTakenDosages(self, dailyDoses):
        textToRead = "today you have taken. "

        for doseTaken in dailyDoses.getTotalTaken():
            textToRead.append("your {0} dose containing. ", doseTaken['name'])
            for medication in doseTaken['medications']:
                textToRead.append("{0} ", medication['name'])

        return textToRead

