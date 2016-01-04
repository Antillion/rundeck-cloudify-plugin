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

from mock import Mock, MagicMock
from mock import patch

from cloudify.workflows import local
from cloudify.exceptions import NonRecoverableError

sys.path.append(os.getcwd() + '/plugin')

import cfyrundeck.jobs as jobs
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

class TestRundeckPlugin(unittest.TestCase):
    def test_simple_call(self):
        with patch('cfyrundeck.jobs.Rundeck') as RundeckMock:
            instance = RundeckMock.return_value
            instance.run_job.return_value = {'id': '0987'}
            instance.execution.side_effect = [{'status':'running'}, {'status':'succeeded'}]

            self.env.execute('install', task_retries=0)

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
