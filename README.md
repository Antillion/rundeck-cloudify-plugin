# rundeck-cloudify-plugin

Simple plugin that allows calling of Rundeck jobs from a Cloudify blueprint

# Installation

Include as a standard Cloudify import; known to work up to Cloudify 3.2.1.

If using a local install with `cfy local create-requirements` then the pip install
needs to be told to use the (deprecated) dependency links as currently this
plugin relies on a custom build of `rundeckrun`. This can be done like so:

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

## antillion.cfyrundeck.jobs.execute (lifecycle operation)

Starts the execution of a Rundeck job and waits for its completion.

In the event of the job failing the operation will error.

### Inputs:

 - `job_id`: required, the ID of the Rundeck job to execute
 - `args`: required, dictionary; name/value pairs of arguments that will be sent to Rundeck
 - `poll_in_s`: optional, the delay between checks of the executing job (default: 10 s)
 - *the Rundeck configuration

## antillion.cfyrundeck.jobs.import_job (workflow operation)

Imports a YAML or XML job description from a remote location into Rundeck.

### Parameters:

 - `file_url`: required, URL to the file containing the job description
 - `project`: required, the name of the project the job should be imported into
 - `format`: required, the format of the job. Either: `yaml` or `xml`
 - `preserve_uuid`: optional, whether to preserve the UUID of the job or create a new one (default: `true`)
 - `rundeck`: required, the Rundeck configuration data

## antillion.cfyrundeck.projects.import_archive

Imports an entire Rundeck project archive into an existing project.

### Parameters:

 - `archive_url`: required, the URL to the archived project
 - `project`: required, name of the project
 - `rundeck`: required, the Rundeck configuration data
