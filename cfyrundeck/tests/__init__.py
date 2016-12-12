import os
from unittest import TestCase

from mock import MagicMock, PropertyMock

from cloudify.mocks import MockCloudifyContext
from cloudify.workflows import local


class PluginTestBase(TestCase):
    def get_mock_context(self, test_name):
        test_node_id = test_name
        test_properties = {
        }

        operation = {
            'retry_number': 0
        }

        ctx = MockCloudifyContext(
            node_id=test_node_id,
            properties=test_properties,
            operation=operation
        )

        return ctx


    def setup_get_mock(self, GetMock, response_status, response_data):
        GetMock.return_value = MagicMock()
        GetMock.return_value.__str__.return_value = response_data
        type(GetMock.return_value).status_code = PropertyMock(
            return_value=response_status)
        type(GetMock.return_value).text = PropertyMock(return_value=response_data)
        type(GetMock.return_value).content = PropertyMock(
            return_value=response_data)

    def setUp(self, blueprint_filename='test_rundeck.yaml', inputs={}):
        self.init_with_blueprint(blueprint_filename, inputs)

    def init_with_blueprint(self, blueprint_filename='test_rundeck.yaml', inputs = {}):
        blueprint_path = os.path.join(os.path.dirname(__file__),
                                      'blueprint', blueprint_filename)

        self.env = local.init_env(blueprint_path,
                                  name=self._testMethodName,
                                  inputs=inputs)
