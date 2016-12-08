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
from rundeck.client import Rundeck

def create_rundeck_client(rundeck_config):
  """Creates a Rundeck client using the 'standardised' format that is expected
  within blueprints.

  :Parameters:
    rundeck_config : dict
      Configuration from a blueprint

  :rtype: rundeck.client.Rundeck
  :return: the correctly-build Rundeck client
  """
  assert rundeck_config.get('hostname') is not None, 'Hostname must be present'
  assert rundeck_config.get('api_token') is not None, 'API token must be present'

  return Rundeck(rundeck_config['hostname'],
                 api_token=rundeck_config['api_token'],
                 protocol=rundeck_config['protocol'] if rundeck_config.has_key('protocol') else 'http',
                 port=rundeck_config['port'] if rundeck_config.has_key('port') else 4440)
