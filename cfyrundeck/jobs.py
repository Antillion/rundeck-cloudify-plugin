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

# ctx is imported and used in operations
from cloudify import ctx
from cloudify.logs import send_task_event
# put the operation decorator on any function that is a task
from cloudify.decorators import operation, workflow
from cloudify.exceptions import NonRecoverableError, RecoverableError

import utils
import time
from requests import get, codes

def search_tree_for_property(curr_node_instance, property_name, default_val=None):
    assert curr_node_instance is not None
    assert property_name is not None

    if property_name in curr_node_instance.runtime_properties:
        return curr_node_instance.runtime_properties[property_name]

    bp_node = curr_node_instance._node

    if property_name in bp_node.properties:
        return bp_node.properties[property_name]

    if len(curr_node_instance.relationships) is 0:
        return default_val

    def for_contained_in(relationship): return relationship.type == 'cloudify.relationships.contained_in'

    contained_in_rels = filter(for_contained_in, curr_node_instance.relationships)

    if len(contained_in_rels) is 0:
        return default_val

    assert len(contained_in_rels) is 1, 'Nodes can only be contained in exactly 1 other node.'

    return search_tree_for_property(contained_in_rels[0].target.instance, property_name, default_val)



@operation
def execute(**kwargs):
    rundeck = utils.create_rundeck_client(kwargs)
    job_id = kwargs['job_id']
    poll_in_s = kwargs['poll_in_s'] if kwargs.has_key('poll_in_s') else 10

    ctx.logger.info("Rundeck[{0}]: Starting`...".format(job_id))
    run_result = rundeck.run_job(job_id, argString=kwargs['args'])

    execution_id = run_result['id']
    ctx.logger.info("Rundeck[{0}]:Execution[{1}] Started...".format(job_id, execution_id))

    status = 'running'
    while status == 'running':
        time.sleep(poll_in_s)
        execution_status = rundeck.execution_status(execution_id)
        ctx.logger.info("Rundeck[{0}]:Execution[{1}] Checked execution, status is: {2}".
                        format(job_id, execution_id, execution_status['status']))
        status = execution_status['status']

    ctx.logger.info("Rundeck[{0}]:Execution[{1}] {2} ".format(job_id, execution_id, status))
    if status != 'succeeded':
        raise NonRecoverableError("Execution [{0}] did not succeed, result was: {1}".format(execution_id, status))

@operation
def execute_v2(**kwargs):
    assert kwargs.get('rundeck_config') is not None, 'Node must have property rundeck_config'
    rundeck = utils.create_rundeck_client(kwargs['rundeck_config'])

    job_id = kwargs['job_id']
    poll_in_s = kwargs['poll_in_s'] if kwargs.has_key('poll_in_s') else 10

    ctx.logger.info("Rundeck[{0}]: Starting`...".format(job_id))
    run_result = rundeck.run_job(job_id, argString=kwargs['args'])

    execution_id = run_result['id']
    ctx.logger.info("Rundeck[{0}]:Execution[{1}] Started...".format(job_id, execution_id))

    status = 'running'
    while status == 'running':
        time.sleep(poll_in_s)
        execution_status = rundeck.execution_status(execution_id)
        ctx.logger.info("Rundeck[{0}]:Execution[{1}] Checked execution, status is: {2}".
                        format(job_id, execution_id, execution_status['status']))
        status = execution_status['status']

    ctx.logger.info("Rundeck[{0}]:Execution[{1}] {2} ".format(job_id, execution_id, status))
    if status != 'succeeded':
        raise NonRecoverableError("Execution [{0}] did not succeed, result was: {1}".format(execution_id, status))


@operation
def import_job(file_url, project, format, preserve_uuid, **kwargs):
  ctx.logger.info('Importing job from {0} to {1}'.format(file_url, project))

  result = get(file_url)
  if result.status_code != codes.ok:
    raise NonRecoverableError('Import failed, status code: {0}, full data: {1}'.format(result.status_code, result))

  rundeck = utils.create_rundeck_client(kwargs['rundeck'])
  import_result = rundeck.import_job(result.text, {'format': format, 'project': project})
  return import_result
