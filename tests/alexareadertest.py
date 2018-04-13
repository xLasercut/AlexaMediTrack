import unittest

from importdata.prescriptions import DailyDosage
from alexareader import UserDataReader

class TestReadUserData(unittest.TestCase):

    TestSource = {
        "userId": "3456788934956734",
        "timeSlots": [{
            "name": "early am",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": "20180511120000",
                "timeBetweenDosages": 4,
                "dose": 2
            }, {
                "name": "pot pourri",
                "taken": None,
                "timeBetweenDosages": 4,
                "dose": 1
            }]
        }, {
            "name": "late am",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": "20180511121000",
                "timeBetweenDosages": 4,
                "dose": 2
            }, {
                "name": "pot pourri",
                "taken": "20180511121200",
                "timeBetweenDosages": 4,
                "dose": 1
            }]
        }, {
            "name": "Early Pm",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": None,
                "timeBetweenDosages": 4,
                "dose": 2
            }, {
                "name": "pot pourri",#
                "timeBetweenDosages": 4,
                "taken": None,
                "dose": 1
            }]
        }, {
            "name": "Late Pm",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": None,
                "timeBetweenDosages": 4,
                "dose": 2
            }]
        }]
    }

    EmptyTestSource = {
        "userId": "3456788934956734",
        "timeSlots": [{
            "name": "early am",
            "medications": []
        }, {
            "name": "late am",
            "medications": []
        }, {
            "name": "Early Pm",
            "medications": []
        }, {
            "name": "Late Pm",
            "medications": []
        }]
    }

    def test_ReadUserData(self):
        dosage = DailyDosage(self.TestSource, None)
        reader = UserDataReader()
        result = reader.readCurrentStatus(dosage)
        self.assertTrue(result)
        self.assertTrue(result != "Your medications list is empty")

    def test_ReadUserDataWhenNoMeds(self):
        dosage = DailyDosage(self.EmptyTestSource, None)
        reader = UserDataReader()
        result = reader.readCurrentStatus(dosage)
        self.assertTrue(result)
        self.assertTrue(result == "Your medications list is empty")

    def test_GetNextDoseTimeWhenDosesToTake(self):
        dosage = DailyDosage(self.TestSource, None)
        reader = UserDataReader()
        result = reader.getNextFullDoseTime(dosage)
        self.assertTrue(result)
        self.assertTrue(result == "You can take your next dose at 16 12")

    def test_GetNextDoseTimeWhenNoDosesToTake(self):
        fullSource = self.TestSource.copy()
        for slot in fullSource['timeSlots']:
            for medication in slot['medications']:
                medication['taken'] = "20180511121000"

        dosage = DailyDosage(self.TestSource, None)
        reader = UserDataReader()
        result = reader.getNextFullDoseTime(dosage)
        self.assertTrue(result)
        self.assertTrue(result == "You have taken all your doses for today")

    def test_GetNextDoseTimeWhenNoDosesTaken(self):
        fullSource = self.TestSource.copy()
        for slot in fullSource['timeSlots']:
            for medication in slot['medications']:
                medication['taken'] = None

        dosage = DailyDosage(self.TestSource, None)
        reader = UserDataReader()
        result = reader.getNextFullDoseTime(dosage)
        self.assertTrue(result)
        self.assertTrue(result == "You have not taken any doses today yet")

if __name__ == '__main__':
    unittest.main()
