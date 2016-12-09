from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from requests import get

import cfyrundeck.utils as utils


def validation_error(msg, causes=[], throw_on_failure=False):
    ctx.logger.error(msg)
    # Accessing protected member. yay.
    ctx._endpoint.send_plugin_event(message=msg,
                                    args=['validation_error'])
    if throw_on_failure:
        raise NonRecoverableError(msg, causes=causes)

@operation
def validate_job(job_id, raise_on_failure=False, **kwargs):
    ctx.logger.info('Validating job {}'.format(ctx.node.properties['job_id']))
    rd_client = utils.create_rundeck_client(ctx.node.properties['rundeck_config'])
    ctx.logger.debug('Conducting pre-check to validate we can talk to Rundeck API')
    rd_client.system_info()
    try:
        ctx.logger.debug('Making GET of job {}'.format(ctx.node.properties['job_id']))
        job = rd_client.api.job(ctx.node.properties['job_id'])
        ctx.logger.debug('Success')
        return True
    except Exception as ex:
        validation_error('Error occurred while attempting to retrieve Rundeck job '
                         '      {}. Error was: {}'.format(ctx.node.properties['job_id'],
                                                    ex),
                         causes=[ex],
                         throw_on_failure=raise_on_failure)


@operation
def validate_config_node(raise_on_failure=False, **kwargs):
    ctx.logger.info('Validating Rundeck configuration of {}'.format(ctx.node.properties))

    endpoint_base_url = '{}://{}:{}'.format(ctx.node.properties['protocol'],
                                ctx.node.properties['hostname'],
                                ctx.node.properties['port'])
    ctx.logger.debug('Attempting to GET {}'.format(endpoint_base_url))
    try:
        endpoint_check = get(endpoint_base_url)
        ctx.logger.debug('Success')
    except Exception as ex:
        validation_error('Error occurred while trying to validate connection '
                                  'to {}. Error was: {}'.format(endpoint_base_url,
                                                                ex),
                         throw_on_failure=raise_on_failure)

    ctx.logger.debug('Attempting to call the Rundeck API (for system info)')
    rd_client = utils.create_rundeck_client(ctx.node.properties)
    try:
        system_info = rd_client.system_info()
        ctx.logger.debug('Success. System info is: {}'.format(system_info))
    except Exception as ex:
        validation_error('Error occurred while trying to validate rundeck login '
                                  'to {}. Error was: {}'.format(endpoint_base_url,
                                                                ex),
                         throw_on_failure=raise_on_failure)