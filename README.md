# rundeck-cloudify-plugin

[![codecov.io](https://codecov.io/github/Antillion/rundeck-cloudify-plugin/coverage.svg?branch=master)](https://codecov.io/github/Antillion/rundeck-cloudify-plugin?branch=master)

[![wercker status](https://app.wercker.com/status/384e7713a3dcd6811bf0a296d975ca27/m "wercker status")](https://app.wercker.com/project/bykey/384e7713a3dcd6811bf0a296d975ca27)

Simple plugin that integrates with [Rundeck](http://rundeck.org).

The following operations are available:

 - Execute (and wait for) a job
 - Import a single job XMl/YAML into a project
 - Import an entire project archive into a project

Known to work with Cloudify 3.4 and - more or less - Rundeck versions API 11+.
Rundeck calls are really forwarded off to an Antillion fork of [(a)rundeckrun](http://github.com/antillion/arundeckrun).

# Installation

Import as a standard Cloudify import; currently using Github as the hosting
repo for the plugin.

For the master (development) branch:

    imports:
      - https://raw.githubusercontent.com/Antillion/rundeck-cloudify-plugin/master/plugin.yaml

You must also declare a node of type `antillion.rundeck.config` somewhere in
your node list. This is a workaround as Cloudify will not properly include the
plugin unless a direct type reference is made from the blueprint.

A simple full example might be:

    tosca_definitions_version: cloudify_dsl_1_3

    imports:
     - https://raw.githubusercontent.com/Antillion/rundeck-cloudify-plugin/master/plugin.yaml

    node_templates:
      rundeck_config: { type: antillion.rundeck.config }


For a particular version the format is very similar, however replace `master`
with the version (like `0.1.1` below). The list of releases is found [here](https://github.com/Antillion/rundeck-cloudify-plugin/releases).

    imports:
      - https://raw.githubusercontent.com/Antillion/rundeck-cloudify-plugin/0.1.1/plugin.yaml

## Local / offline deployment

If using a local install, such as a Cloudify bootstrap deployment, with
`cfy local create-requirements` then `pip install` needs to be told to use the
(deprecated) dependency links as currently this plugin relies on a custom build
of `rundeckrun`. This can be done like so:

    pip install --process-dependency-links -r requirements.txt

# Usage

All operations require information about where the Rundeck instance is; each
operation follows a (nearly) standard way of having the data supplied.

All require the following common data with the names specified:

 - `hostname`: required, the name (or IP address) of the Rundeck instance
 - `api_token`: required, the API token used to make API calls
 - `port`: optional, the port that Rundeck is listening on (default: 4440)
 - `protocol`: optional, protocol to use (default: http for 80, https for 443)


Lifecycle interfaces require the data as an input.
Workflow operations require the data under a simple dictionary named `rundeck`.

## antillion.cfyrundeck.jobs.execute (operation)

Starts the execution of a Rundeck job and waits for its completion.

In the event of the job failing the operation will error.

### Inputs:

 - `job_id`: required, the ID of the Rundeck job to execute
 - `args`: required, dictionary; name/value pairs of arguments that will be sent to Rundeck
 - `poll_in_s`: optional, the delay between checks of the executing job (default: 10 s)
 - *the Rundeck configuration

### Example

    node_templates:
      rundeck_node_example:
        type: cloudify.nodes.Root
        interfaces:
          cloudify.interfaces.lifecycle:
            create:
              implementation: antillion.cfyrundeck.jobs.execute
              inputs:
                hostname: 'some.rundeck.host'
                api_token: 'very-long-api-token'
                port: 24440
                protocol: http
                job_id: job-ids-are-very-long-too
                args:
                  stringArg: 'stringVal1, stringVal2'
                  numArg: 3
                  arrayArg: # This will be concatenated into a comma-deliniated string
                    - 3
                    - 4
                    - 5



## antillion.cfyrundeck.jobs.import_job (operation)

Imports a YAML or XML job description from a remote location into Rundeck.

### Parameters:

 - `file_url`: required, URL to the file containing the job description
 - `project`: required, the name of the project the job should be imported into
 - `format`: required, the format of the job. Either: `yaml` or `xml`
 - `preserve_uuid`: optional, whether to preserve the UUID of the job or create a new one (default: `true`)
 - `rundeck`: required, the Rundeck configuration data

## antillion.rundeck.import_job (workflow)

See above operation for parameters details.

### Example

Local (bootstrap) execution:

    cfy local execute -w antillion.rundeck.import_job \
                      -p '{"file_url": "http://some.host/rundeck_job_file.yaml", \
                           "project": "my_project", "format": "yaml", \
                           "rundeck": {"hostname": "my.rundeck", \
                                       "api_token": "mega-long-api-token"}}'

Or, of course:

    cfy executions start -w antillion.rundeck.import_job \
                         -d YOUR_DEPLOYMENT_ID\
                         -p '{"file_url": "http://some.host/rundeck_job_file.yaml", \
                              "project": "my_project", "format": "yaml", \
                              "rundeck": {"hostname": "my.rundeck", \
                                          "api_token": "mega-long-api-token"}}'


## antillion.cfyrundeck.projects.import_archive (operation)

Imports an entire Rundeck project archive into an existing project.

### Parameters:

 - `archive_url`: required, the URL to the archived project
 - `project`: required, name of the project
 - `rundeck`: required, the Rundeck configuration data


## antillion.rundeck.import_project_archive (workflow)


See above operation for parameters details.

 ### Example

Local execution:

     cfy local execute -w antillion.rundeck.import_project_archive \
                       -p '{"archive_url": "http://some.host/my_project.jar", \
                            "project": "my_project", \
                            "rundeck": {"hostname": "my.rundeck", \
                                        "api_token": "mega-long-api-token"}}'

Standard execution:

    cfy executions start -w antillion.rundeck.import_project_archive \
                         -d YOUR_DEPLOYMENT_ID\
                         -p '{"archive_url": "http://some.host/my_project.jar", \
                              "project": "my_project", \
                              "rundeck": {"hostname": "my.rundeck", \
                                          "api_token": "mega-long-api-token"}}'


# Development

Based on the standard Cloudify starter plugin so follow their guidelines on
development.

Testing is performed via tox; targets Python 2.7 only at present.

Assuming tox is installed, simply run:

    tox

And the (basic) unit tests should run.

To run a single test, append `-- path/to/test`, like so:

    tox -- cfyrundeck/tests/test_jobs.py
