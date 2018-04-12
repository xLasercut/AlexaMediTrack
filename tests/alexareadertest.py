import unittest

from importdata.prescriptions import DailyDosage

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

    def test_ReadUserData(self):
        dosage = DailyDosage(self.TestSource, None)
        timeSlots = dosage.getAllMedicationTaken()
        self.assertEqual(len(timeSlots), 2)
        self.assertEqual(len(timeSlots[0]['medications']), 1)
        self.assertEqual(len(timeSlots[1]['medications']), 2)



if __name__ == '__main__':
    unittest.main()
