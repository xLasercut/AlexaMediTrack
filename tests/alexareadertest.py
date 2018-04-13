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
                "dose": 2
            }, {
                "name": "pot pourri",
                "taken": None,
                "dose": 1
            }]
        }, {
            "name": "late am",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": "20180511120000",
                "dose": 2
            }, {
                "name": "pot pourri",
                "taken": "20180511120000",
                "dose": 1
            }]
        }, {
            "name": "Early Pm",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": None,
                "dose": 2
            }, {
                "name": "pot pourri",
                "taken": None,
                "dose": 1
            }]
        }, {
            "name": "Late Pm",
            "medications": [{
                "name": "Dried Frog Pills",
                "taken": None,
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

if __name__ == '__main__':
    unittest.main()
