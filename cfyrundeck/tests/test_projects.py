########
# Copyright (c) 2016 Antillion Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import sys
import os

import unittest
import importlib

from mock import Mock, MagicMock, PropertyMock
from mock import patch

from cloudify.workflows import local
from cloudify.exceptions import NonRecoverableError

sys.path.append(os.getcwd() + '/cfyrundeck')

import cfyrundeck.jobs as jobs
import cfyrundeck.projects as projects
from rundeck.client import Rundeck

#
# Enable mocking of importlib.import_module so we can intercept calls to
# our own plugin
_import_module = importlib.import_module

def mocked_import(arg):
  """Intercepts imports and returns our own copy of plugin.tasks (if requested)"""
  if arg == 'cfyrundeck.jobs':
    return tasks
  elif arg == 'rundeck.client':
    return Rundeck
  else:
    print 'Allowing import: {0}'.format(arg)
    return _import_module(arg)

def mocked_rundeck():
  return 1

def get_blueprint_path():
  return os.getcwd() + '/cfyrundeck/tests/blueprint'


class TestRundeckPlugin(unittest.TestCase):

  def setup_get_mock(self, GetMock, response_status, response_data):
    GetMock.return_value = MagicMock()
    GetMock.return_value.__str__.return_value = response_data
    type(GetMock.return_value).status_code = PropertyMock(return_value=response_status)
    type(GetMock.return_value).text = PropertyMock(return_value=response_data)
    type(GetMock.return_value).content = PropertyMock(return_value=response_data)

  def test_import_archive(self):
    with patch('cfyrundeck.utils.Rundeck') as RundeckMock, patch('cfyrundeck.projects.get') as GetMock:#, open('{0}/{1}'.format(get_blueprint_path(), job_filename), 'r') as blueprint_file:
      instance = RundeckMock.return_value
      self.setup_get_mock(GetMock, 200, 'test')
      instance.return_value.import_project_archive.return_value = True

      workflow_parameters = {'project': 'stove', 'archive_url': 'http://archive_url',
                             'rundeck': {'hostname': 'rundeck.example.com', 'api_token': 'SOME_API_TOKEN'}}
      self.env.execute('antillion.rundeck.import_project_archive', parameters=workflow_parameters)

      RundeckMock.assert_called_once_with('rundeck.example.com',
                                          api_token='SOME_API_TOKEN',
                                          port=4440, protocol='http')
      GetMock.assert_called_once_with(workflow_parameters['archive_url'])
      instance.import_project_archive.assert_called_once_with(
        workflow_parameters['project'], 'test'
      )

  def setUp(self):
    blueprint_path = os.path.join(os.path.dirname(__file__),
                                  'blueprint', 'test_rundeck.yaml')
    inputs = {}
    self.env = local.init_env(blueprint_path,
                              name=self._testMethodName,
                              inputs=inputs)
