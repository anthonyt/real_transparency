from realt.tests import *

class TestXmlimportController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='xmlimport', action='index'))
        # Test response...
