#!/bin/bash
CFY_IP=${CFY_IP:-192.168.0.201}
BP_PATH=${BP_PATH:-remote-example.blueprint.yaml}
PLUGIN_NAME=${PLUGIN_NAME:-rundeck-cloudify-plugin}
REUPLOAD_PLUGIN=${REUPLOAD_PLUGIN:-yes}
PARAMETERS=$1
DEPLOY_ID=${DEPLOY_ID:-$(date "+%d_%H%M")}

if [ "$PARAMETERS" = "" ]; then
    echo "FATAL: no parameter string specified"
    echo "Usage: deploy.sh \"parameter string\""
    exit 1
fi

echo "Starting local file server, assuming on 192.168.0.190:8000"
curr_dir=$(pwd)
cd ..
python -m SimpleHTTPServer &
FS_PID=$!

make build_wagons

cd $curr_dir

cfy use -t ${CFY_IP}

if [ "$REUPLOAD_PLUGIN" == "yes" ]; then
    echo "Deleting plguin ${PLUGIN_NAME} (if it exists)"
    cfy plugins delete -f -p $(cfy plugins list | grep ${PLUGIN_NAME} | awk '{ print $2 }') || echo "Plugin ${PLUGIN_NAME} not yet present"
    for wagon in $(ls ../*.wgn); do
        echo "Uploading plugin ${wagon}"
        cfy plugins upload -p $wagon -v
    done
fi


echo "Validating ${BP_PATH}"
cfy blueprints validate -p ${BP_PATH}

echo "Starting install of ${BP_PATH}"
cfy blueprints upload  -v -p ${BP_PATH}   -b ${DEPLOY_ID}
cfy deployments create -v -b ${DEPLOY_ID} -d ${DEPLOY_ID} -i ${PARAMETERS}
#sleep 30
#cfy executions start   -v -d ${DEPLOY_ID} --include-logs -w execute_operation \
#                       -p "operation=cloudify.interfaces.validation.creation"

#cfy executions start   -v -d ${DEPLOY_ID} --include-logs -w install

kill $FS_PID