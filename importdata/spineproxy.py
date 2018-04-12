import os
import json

class SpineProxy(object):
    DAILY_DOSAGE_KEY = "dailyDosage"
    DOSAGE_KEY = "dosage"
    COURSE_KEY = "course"
    NAME_KEY = "name"
    MEDICATION_KEY = "medications"

class FakeSpineProxy(SpineProxy):

    FAKE_DATA_SOURCE = "fakespinedata.json"
    EMPTY_PRESCRIPTION = {SpineProxy.MEDICATION_KEY : []}

    def __init__(self):
        self.dataSource = self._loadData()

    def _loadData(self):
        dataSource = {}
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.FAKE_DATA_SOURCE)
        with open(path, "r") as source:
            dataSource = json.loads(source.read())

        return dataSource

    def getPrescriptions(self, nhsNumber):
        """ Gets all prescriptions from spine """
        return self.dataSource.get(nhsNumber, self.EMPTY_PRESCRIPTION)
