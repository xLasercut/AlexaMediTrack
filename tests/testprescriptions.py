import unittest
from importdata.prescriptions import PrescriptionFinder, TimeSlices
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
            self.assertEquals(slot["taken"], None)
            self.assertTrue(slot["name"] in TimeSlices.getFourSlots())


if __name__ == '__main__':
    unittest.main()
