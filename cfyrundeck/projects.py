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

from requests import get, codes

@operation
def import_archive(project, archive_url, preserve_uuid, import_executions, import_config, import_acls, **kwargs):
  ctx.logger.info('[{1}] - Importing project archive from {0}'.format(archive_url, project))

  result = get(archive_url)
  if result.status_code != codes.ok:
    raise NonRecoverableError('Import failed, status code: {0}, full data: {1}'.format(result.status_code, result))

  rundeck = Rundeck(kwargs['rundeck']['hostname'], api_token=kwargs['rundeck']['api_token'])
  rundeck.project_archive_import(project, result.content)
