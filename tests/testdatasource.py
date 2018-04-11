import unittest
import os
import json
from datasource import UserDataSource
import shutil
from pystache import render

from datetime import datetime

class TestUserDataSource(unittest.TestCase):
    TEST_DATA_FILE = "testuserdatatemplate.json"
    SAVE_FOLDER = "userdata"

    DATA = {
        "date": "20180410",
        "userId": "148127345172897",
        "timeSlots": [{
            "name": "EarlyAM",
            "taken": "20180410084420",
            "medications": [{
                "name": "dried frog pills",
                "dose": "1"
            }]
        },
            {
                "name": "LateAM",
                "taken": "20180410124420",
                "medications": [{
                    "name": "dried frog pills",
                    "dose": "1"
                },
                    {
                        "name": "Aufero capitis",
                        "dose": "1"
                    }]
            },
            {
                "name": "EarlyPM",
                "taken": "20180410154420",
                "medications": [{
                    "name": "dried frog pills",
                    "dose": "1"
                }]
            },
            {
                "name": "LatePM",
                "taken": "None",
                "medications": [{
                    "name": "dried frog pills",
                    "dose": "1"
                },
                    {
                        "name": "Aufero capitis",
                        "dose": "1"
                    }]
            }]}

    def setUp(self):
        if not os.path.isdir(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)

    def tearDown(self):
        if os.path.isdir(self.SAVE_FOLDER):
            shutil.rmtree(self.SAVE_FOLDER)

    def test_UserDataSourceSave(self):
        userDataSource = UserDataSource()
        userId = "qwe-3456"

        userDataSource.save(userId, self.DATA)

    def test_UserDataSourceLoad(self):
        userDataSource = UserDataSource()
        userId = "qwe-1111"

        expectedDate = datetime.now().strftime("%Y%m%d")
        self._setupSource(expectedDate, userId)

        result = userDataSource.load(userId)

        self.assertEquals(result['date'], expectedDate)

    def _setupSource(self, date, userId):
        data = None
        targetPath = self.SAVE_FOLDER + "/" + userId + ".json"
        with open(self.TEST_DATA_FILE, "r") as file:
            data = file.read()

        data = render(data, {"date" : date, "userId" : userId})

        with open(targetPath, "w") as file:
            file.write(data)


if __name__ == '__main__':
    unittest.main()
