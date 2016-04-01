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

# ctx is imported and used in operations
from cloudify import ctx

# put the operation decorator on any function that is a task
from cloudify.decorators import operation, workflow
from cloudify.exceptions import NonRecoverableError

from rundeck.client import Rundeck
import time
#
# @operation
# def execute(**kwards):
#     rundeck = Rundeck(kwards['rundeck_server'], api_token=kwards['api_token'])
#     job_id = kwards['job_id']
#     ctx.logger.info("Rundeck[{0}]: Starting`...".format(job_id))
#     run_result = rundeck.run_job(job_id, argString=kwards['args'])
#
#     execution_id = run_result['id']
#     ctx.logger.info("Rundeck[{0}]:Execution[{1}] Started...".format(job_id, execution_id))
#
#
#     poll_in_s = kwards['poll_in_s'] if kwards.has_key('poll_in_s') else 10
#     status = 'running'
#     while status == 'running':
#         time.sleep(poll_in_s)
#         execution_status = rundeck.execution(execution_id)
#         status = execution_status['status']
#
#     ctx.logger.info("Rundeck[{0}]:Execution[{1}] {2} ".format(job_id, execution_id, status))
#     if status != 'succeeded':
#         raise NonRecoverableError("Execution [{0}] did not succeed, result was: {1}".format(execution_id, status))

@operation
def import_archive(archive_url, preserve_uuid, import_executions, import_config, import_acls, **kwargs):
  ctx.logger.info('Importing project archive from {0}'.format(archive_url))
