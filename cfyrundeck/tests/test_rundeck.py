########
# Copyright (c) 2015 Antillion Ltd. All rights reserved
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

  # def test_import_archive(self):
  #   with patch('cfyrundeck.jobs.Rundeck') as RundeckMock:
  #     instance = RundeckMock.return_value
  #     instance.run_job.return_value = {'id': '0987'}
  #     instance.execution.side_effect = [{'status':'running'}, {'status':'succeeded'}]
  #
  #     self.env.execute('import_project', parameters={'archive_url': 'archive_url'})

  def setup_get_mock(self, GetMock, response_status, response_data):
    GetMock.return_value = MagicMock()
    GetMock.return_value.__str__.return_value = response_data
    type(GetMock.return_value).status_code = PropertyMock(return_value=response_status)
    type(GetMock.return_value).text = PropertyMock(return_value=response_data)

  def build_import_params(self, job_filename):
    file_url = 'http://localhost:54321/blueprint/{0}'.format(job_filename)
    return {
      'file_url': file_url,
      'project': 'project', 'format': 'xml',
      'rundeck': {'hostname': 'rundeck.example.com', 'api_token': 'SOME_API_TOKEN'}
    }


  def test_import_with_missing_file(self):
    job_filename = 'import_job_simple.xml'
    with patch('cfyrundeck.jobs.Rundeck') as RundeckMock, patch('cfyrundeck.jobs.get') as GetMock:
      job_data = '<some><job><data></data></job></some>'
      instance = RundeckMock.return_value
      instance.jobs_import.return_value = {}

      self.setup_get_mock(GetMock, 400, '')

      import_params = self.build_import_params(job_filename)

      with self.assertRaises(NonRecoverableError) as cm:
        self.env.execute('import_job', parameters=import_params)

      GetMock.assert_called_once_with(import_params['file_url'])
      instance.import_job.assert_not_called()

  def test_import(self):
    job_filename = 'import_job_simple.xml'
    with patch('cfyrundeck.jobs.Rundeck') as RundeckMock, patch('cfyrundeck.jobs.get') as GetMock:
      job_data = '<some><job><data></data></job></some>'
      instance = RundeckMock.return_value
      instance.jobs_import.return_value = {}

      self.setup_get_mock(GetMock, 200, job_data)

      import_params = self.build_import_params(job_filename)

      self.env.execute('import_job', parameters=import_params)

      RundeckMock.assert_called_once_with('rundeck.example.com', api_token='SOME_API_TOKEN')
      GetMock.assert_called_once_with(import_params['file_url'])
      instance.import_job.assert_called_once_with(job_data, { 'project': 'project', 'format': 'xml'})


    # with patch('cfyrundeck.jobs.Rundeck') as RundeckMock:
    #   instance = RundeckMock.return_value
    #   execution_id = '0987'
    #   instance.run_job.return_value = {'id': execution_id}
    #   instance.execution.side_effect = []
    #   self.env.execute('install', task_retries=0)
    #   self.env.execute('import_job', parameters={'file_url': '', 'project': 'project', 'format': 'yaml'})

  def test_simple_call(self):
    with patch('cfyrundeck.jobs.Rundeck') as RundeckMock:
      instance = RundeckMock.return_value
      instance.run_job.return_value = {'id': '0987'}
      instance.execution.side_effect = [{'status':'running'}, {'status':'succeeded'}]

      self.env.execute('install', task_retries=0)
      RundeckMock.assert_called_once_with('rundeck.example.com', api_token='SOME_API_TOKEN')

      instance.run_job.assert_called_once_with('ASDF-ASDFASDFD-ASDFASDF-ASDFASDF',
                                               argString={'stringArg': 'stringVal1, stringVal2',
                                                          'arrayArg': [3,4,5],
                                                          'numArg': 2})


  def test_execution_failure(self):
    with patch('cfyrundeck.jobs.Rundeck') as RundeckMock:
      instance = RundeckMock.return_value
      execution_id = '0987'
      instance.run_job.return_value = {'id': execution_id}
      result = 'failed'
      instance.execution.side_effect = [{'status':'running'}, {'status':result}]
      expected_exception_msg = "Workflow failed: Task failed 'cfyrundeck.jobs.execute' -> Execution [{0}] did not succeed, result was: {1}".format(execution_id, result)
      with self.assertRaises(RuntimeError) as cm:
        self.env.execute('install', task_retries=0)

      self.assertEquals(expected_exception_msg, str(cm.exception))

  def setUp(self):
    blueprint_path = os.path.join(os.path.dirname(__file__),
                                  'blueprint', 'test_rundeck.yaml')
    inputs = {}
    self.env = local.init_env(blueprint_path,
                              name=self._testMethodName,
                              inputs=inputs)
