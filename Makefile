include env_make
VERSION ?= 0.2.1
PLUGIN_NAME = rundeck-cloudify-plugin
REMOVE_ENV_PATH= "~/cfy-env"
.PHONY: archive


.PHONY: build_task

build_wagons:
	docker run -it --rm  --volume $$(pwd):/wagon --workdir /wagon antillion/wagon-builders:centos-7 wagon create -f -s .

setup_devenv:
	virtualenv env
	pip install -r requirements.txt
	pip install -r test-requirements.txt
	pip install -r dev-requirements.txt
	pip ipython

clear_plugin: ## Clears the plugin from the server. Only clears the first result however.
	cfy init -r
	cfy use -t $(REMOTE_SERVER)
	-cfy plugins delete -f -p $$(cfy plugins list | grep $(PLUGIN_NAME) | awk '{ print $$2 }')

remote_wagon: clear_plugin build_task copy_to_target ## Builds the wagon & uploads it on REMOTE_SERVER
	@echo "Building plugin on $(REMOTE_SERVER)"
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) 'source ~/env/bin/activate && wagon create -f -s $(PLUGIN_NAME)/ -a "--process-dependency-links"'
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) \
		'source $(REMOVE_ENV_PATH)/bin/activate && cfy plugins upload -p $(subst -,_,$(PLUGIN_NAME))*'

copy_to_target: ## Copies the source to the remote server
	-scp -r . $(REMOTE_USER)@$(REMOTE_SERVER):~/$(PLUGIN_NAME)

default: build_task

archive: ## Builds the plugin into a zip file
	#zip -r -0 -x=".git" $(PLUGIN_NAME)-$(VERSION).zip *
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "cd $(PLUGIN_NAME) && zip -r -0 -x='.git' $(PLUGIN_NAME)-$(VERSION).zip *"
	ssh $(REMOTE_USER)@$(REMOTE_SERVER) "sudo mv $(PLUGIN_NAME)/$(PLUGIN_NAME)-$(VERSION).zip /var/stove/fileserver/"

#default: archive