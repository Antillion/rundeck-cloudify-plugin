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

from mock import patch

from requests.exceptions import HTTPError

sys.path.append(os.getcwd() + '/cfyrundeck')

from . import PluginTestBase

class TestJobValidators(PluginTestBase):

  def setUp(self):
    self.rundeck_parameters = {'hostname': 'somehostname',
                               'api_token': 'whee'}
    self.rundeck_defaults = {'protocol': 'http',
                             'port': 4440}
    self.init_with_blueprint('test_job_validation.yaml', inputs=self.rundeck_parameters)



  def test_validate_job(self):
    with patch('cfyrundeck.utils.Rundeck') as rundeck_mock:
      rundeck_mock.return_value.api.job.return_value = {'some': 'return'}

      self.env.execute('execute_operation',
                       parameters={'operation': 'cloudify.interfaces.validation.creation'},
                       task_retries=0)

      rundeck_mock.return_value.api.job.asset_called_once()

  def test_validate_job(self):
    with patch('cfyrundeck.utils.Rundeck') as rundeck_mock:
      rundeck_mock.return_value.api.job.side_effect = HTTPError()

      with self.assertRaises(RuntimeError):
        self.env.execute('execute_operation',
                         parameters={'operation': 'cloudify.interfaces.validation.creation'},
                         task_retries=0)



class TestConfigValidators(PluginTestBase):

  def setUp(self):
    self.rundeck_parameters = {'hostname': 'somehostname',
                               'api_token': 'whee'}
    self.rundeck_defaults = {'protocol': 'http',
                             'port': 4440}
    self.init_with_blueprint('test_config_validation.yaml', inputs=self.rundeck_parameters)


  def test_validate_config_node(self):
    with patch('cfyrundeck.utils.Rundeck') as rundeck_mock, \
         patch('cfyrundeck.validators.get') as get_mock:

      self.env.execute('execute_operation',
                       parameters={'operation': 'cloudify.interfaces.validation.creation'},
                       task_retries=0)

      rundeck_mock.assert_called_once_with(self.rundeck_parameters['hostname'],
                                           api_token=self.rundeck_parameters['api_token'],
                                           protocol=self.rundeck_defaults['protocol'],
                                           port=self.rundeck_defaults['port'])

      get_mock.assert_called_once_with('{}://{}:{}'.format(self.rundeck_defaults['protocol'],
                                                           self.rundeck_parameters['hostname'],
                                                           self.rundeck_defaults['port']))

  def test_validate_config_node_get_fails(self):
    with patch('cfyrundeck.utils.Rundeck') as rundeck_mock, \
         patch('cfyrundeck.validators.get') as get_mock:

      get_mock.side_effect = HTTPError()
      with self.assertRaises(RuntimeError):
        self.env.execute('execute_operation',
                         parameters={'operation': 'cloudify.interfaces.validation.creation'},
                         task_retries=0)

      rundeck_mock.assert_not_called()
      get_mock.assert_called_once()

  def test_validate_config_node_rundeck_fails(self):
    with patch('cfyrundeck.utils.Rundeck') as rundeck_mock, \
            patch('cfyrundeck.validators.get'):

      rundeck_mock.return_value.system_info.side_effect = RuntimeError()

      with self.assertRaises(RuntimeError):
        self.env.execute('execute_operation',
                         parameters={'operation': 'cloudify.interfaces.validation.creation'},
                         task_retries=0)

