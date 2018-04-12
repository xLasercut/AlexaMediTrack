import unittest
from importdata.prescriptions import PrescriptionFinder, TimeSlices, DailyDosage
from importdata.spineproxy import FakeSpineProxy
from datetime import datetime


class TestPrescriptionFinder(unittest.TestCase):
    def test_PrescriptionFinderGetPrescriptions(self):
        spineProxy = FakeSpineProxy()
        userDataSource = None
        userId = "54564564564"
        finder = PrescriptionFinder(spineProxy, userDataSource)
        result = finder.getPrescriptions(userId)

        self.assertEquals(result.userId, userId)
        self.assertEquals(len(result.timeSlots), 5)
        self.assertEquals(result.date, datetime.now().strftime("%Y%m%d"))

        for slot in result.timeSlots:
            self.assertTrue(slot["name"] in TimeSlices.getFourSlots())
            self.assertTrue(slot["medication"])

class TestDailyDosage(unittest.TestCase):

    TestSource = {
        "userId" : "3456788934956734",
        "timeSlots" : [{
            "name" : "Early Am",
            "medications" : [{
                "name" : "Dried Frog Pills",
                "taken" : "20180511120000",
                "dose" : 2
            }, {
                "name" : "pot pourri",
                "taken" : None,
                "dose" : 1
            }]
        },{
            "name" : "Late Am",
            "medications" : [{
                "name" : "Dried Frog Pills",
                "taken" : "20180511120000",
                "dose" : 2
            }, {
                "name" : "pot pourri",
                "taken" : "20180511120000",
                "dose" : 1
            }]
        },{
            "name" : "Early Pm",
            "medications" : [{
                "name" : "Dried Frog Pills",
                "taken" : None,
                "dose" : 2
            }, {
                "name" : "pot pourri",
                "taken" : None,
                "dose" : 1
            }]
        },{
            "name" : "Late Pm",
            "medications" : [{
                "name" : "Dried Frog Pills",
                "taken" : None,
                "dose" : 2
            }]
        }]
    }

    def test_DailyDosageGetAllTaken(self):
        dosage = DailyDosage(self.TestSource, None)
        timeSlots = dosage.getAllMedicationTaken()
        self.assertEqual(len(timeSlots), 2)
        self.assertEqual(len(timeSlots[0]['medications']), 1)
        self.assertEqual(len(timeSlots[1]['medications']), 2)

    def test_DailyDosageGetAllNotTaken(self):
        dosage = DailyDosage(self.TestSource, None)
        timeSlots = dosage.getAllMedicationNotTaken()
        self.assertEqual(len(timeSlots), 3)
        self.assertEqual(len(timeSlots[0]['medications']), 1)
        self.assertEqual(len(timeSlots[1]['medications']), 2)
        self.assertEqual(len(timeSlots[2]['medications']), 1)


if __name__ == '__main__':
    unittest.main()
