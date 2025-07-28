# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

.DEFAULT_GOAL := help
SHELL := /bin/bash

DEFAULTS.NODE_VERSION := $(shell cat .nvmrc 2> /dev/null)
DEFAULTS.PYTHON_VERSION := $(shell cat .python-version)

NODE_VERSION ?= ${DEFAULTS.NODE_VERSION}
PYTHON_VERSION ?= ${DEFAULTS.PYTHON_VERSION}

include makefiles/common_config.mk
include makefiles/global_targets.mk

## ========================================================
## INCLUDE MODULE'S MAKEFILE TARGETS
## ========================================================
module_name-target: ## Call a module make target. Run "make module_name-help" for target lists. Run "ls source/modules" for module list.

# Create a target with the naming convention module_name-target, where $1=target and $2=path to module directory (**/module_name)
define create-target
$(lastword $(subst /, ,$2))-$1:
	@$(MAKE) -C $2 -f Makefile $1
endef

MODULES := source/lib $(shell find ${SOLUTION_PATH}/source/modules -maxdepth 1 -mindepth 1 -type d -not -name __pycache__)
GLOBAL_TARGETS := $(shell grep -E '^[a-zA-Z0-9-]+:' ${SOLUTION_PATH}/makefiles/global_targets.mk | awk -F: '/^[^.]/ {print $$1;}')
MODULE_TARGETS := $(shell grep -E '^[a-zA-Z0-9-]+:' ${SOLUTION_PATH}/makefiles/module_targets.mk | awk -F: '/^[^.]/ {print $$1;}')

$(foreach module,$(MODULES),$(foreach target,$(shell grep -E '^[a-zA-Z0-9-]+:' $(module)/Makefile | awk -F: '/^[^.]/ {print $$1;}'),$(eval $(call create-target,$(target),$(module))))) # For each module, create root target for each module target
$(foreach module,$(MODULES),$(foreach target,$(GLOBAL_TARGETS),$(eval $(call create-target,$(target),$(module))))) # For each module, create targets from global_targets.mk
$(foreach module,$(MODULES),$(foreach target,$(MODULE_TARGETS),$(eval $(call create-target,$(target),$(module))))) # For each module, create targets from module_targets.mk

## ========================================================
## INVOKE MAKE TARGET FROM EACH MODULES' MAKEFILE
## ========================================================
SubMakefiles    = $(shell find source \( -name deployment -o -name cdk.out -o -name .venv -o -name node_modules -o -path **/backstage/cdk \) -prune -false -o -name Makefile)
SubMakeDirs     = $(filter-out ${SOLUTION_PATH},$(dir $(SubMakefiles)))
Prereqs         = source/modules/vpc/ source/modules/auth_setup/ source/modules/cms_config/ source/modules/cms_auth/ source/modules/cms_connect_store/ source/modules/cms_alerts/ source/modules/cms_api/
DeployableDirs  = $(filter-out source/lib/ source/modules/backstage source/modules/cms_ui ${Prereqs},${SubMakeDirs})

define run-module-target
	run_make_with_logging() { \
		output=$$(make -C "$$1" $1 2>&1); \
		module_target_exit_code=$$?; \
		if [[ $$module_target_exit_code -ne 0 ]]; then \
			printf "%bFailed %s\n%s\n%b\n" "${RED}" "$$1" "$$output" "${NC}"; \
		else \
			printf "%bFinished %s%b\n" "${GREEN}" "$$1" "${NC}"; \
		fi; \
		return $$module_target_exit_code; \
	}; \
	did_make_target_fail=0; \
	process_pids=(); \
	IFS=' ' read -a s <<< "$2"; \
	bs=5; \
	printf "%b\nCalling \"make %s\" for each module.%b\n" "${MAGENTA}" "$1" "${NC}"; \
	for ((i=0; i<=$${#s[@]}; i+=bs)); do \
		for module in "$${s[@]:i:bs}"; do \
			(run_make_with_logging "$$module") & process_pids+=($$!); \
		done; \
		for pid in $${process_pids[@]}; do wait "$${pid}" || did_make_target_fail=1; done; \
		process_pids=(); \
	done; \
	exit $$did_make_target_fail;
endef

.PHONY: upgrade
upgrade: root-lock ## Call root and all modules' "make upgrade". Upgrades all lock files without installing dependencies.
	@printf "%b\nUpgrading all module lock files.%b\n" "${MAGENTA}" "${NC}"
	@$(call run-module-target,upgrade,${SubMakeDirs})
	@printf "%b\nFinished upgrading lock files for entire solution.%b\n" "${GREEN}" "${NC}"
	@printf "%bRun %b\"make install\"%b to install upgraded dependencies.%b\n" "${YELLOW}" "${CYAN}" "${YELLOW}" "${NC}"

.PHONY: install
install: root-sync ## Call root and all modules' "make install". Installs all dependencies needed to build the solution.
	@printf "%b\nInstalling dependencies from all module lock files.%b\n" "${MAGENTA}" "${NC}"
	@printf "%bTo instead upgrade lock files and node dependencies, run %b\"make upgrade\"%b first.%b\n" "${YELLOW}" "${CYAN}" "${YELLOW}" "${NC}"
	@$(call run-module-target,install,${SubMakeDirs})
	@printf "%b\nFinished installing dependencies from lock files for entire solution.%b\n" "${GREEN}" "${NC}"

.PHONY: build
build: ## Builds all modules, copies assets to top level deployment folder, then zips the Backstage assets.
	@printf "%bBuilding solution.%b\n" "${MAGENTA}" "${NC}"
	@printf "%b\nStarting module-level builds.%b\n" "${MAGENTA}" "${NC}"
	@$(call run-module-target,build,${SubMakeDirs})
	@printf "%b\nFinished module-level builds.%b\n" "${GREEN}" "${NC}"
	@$(MAKE) asset-copy
	@$(MAKE) zip-backstage-assets
	@printf "%b\nFinished build for entire solution.%b\n" "${GREEN}" "${NC}"
	@printf "%b\nSee %b\"./deployment/global-s3-assets\"%b and %b\"./deployment/regional-s3-assets\"%b for built assets.%b\n" "${YELLOW}" "${CYAN}" "${YELLOW}" "${CYAN}" "${YELLOW}" "${NC}"
	@printf "%bRun %b\"make upload\"%b to upload assets to S3.%b\n" "${YELLOW}" "${CYAN}" "${YELLOW}" "${NC}"

.PHONY: deploy
deploy: ## Call all modules' "make deploy". Order enforced.
	@printf "%bStarting deploy.%b\n" "${MAGENTA}" "${NC}"
	@for dir in $(Prereqs); do \
		printf "%bDeploying %s.%b\n" "${MAGENTA}" "$$dir" "${NC}"; \
		$(MAKE) -C $$dir deploy || exit $$?; \
	done
	@$(call run-module-target,deploy,${DeployableDirs})
	@printf "%b\nFinished deploy for entire solution.%b\n" "${GREEN}" "${NC}"
	@printf "%bView status: %bhttps://%s.console.aws.amazon.com/cloudformation/home?region=%s%b\n" "${YELLOW}" "${CYAN}" "${AWS_REGION}" "${AWS_REGION}" "${NC}"

.PHONY: destroy
destroy: ## Call all modules' "make destroy". Order enforced.
	@printf "%bStarting destroy.%b\n" "${MAGENTA}" "${NC}"
	@$(call run-module-target,destroy,${DeployableDirs})
	@reversed=$$(printf "%s\n" ${Prereqs} | tail -r | xargs echo); \
	for dir in $${reversed}; do \
		printf "%bDestroying %s.%b\n" "${MAGENTA}" "$$dir" "${NC}"; \
		$(MAKE) -C $$dir destroy || exit $$?; \
	done
	@printf "%b\nFinished destroy for entire solution.%b\n" "${GREEN}" "${NC}"
	@printf "%bView status: %bhttps://%s.console.aws.amazon.com/cloudformation/home?region=%s%b\n" "${YELLOW}" "${CYAN}" "${AWS_REGION}" "${AWS_REGION}" "${NC}"

.PHONY: upload
upload: create-upload-bucket upload-backstage-assets-zip ## Call root and all modules' "make upload" and upload backstage assets zip.
	@$(call run-module-target,upload,${SubMakeDirs})
	@printf "%b\nFinished upload for entire solution.%b\n" "${GREEN}" "${NC}"
	@printf "%b\nView resources: %bhttps://s3.console.aws.amazon.com/s3/buckets/%s-%s?region=%s%b\n" "${YELLOW}" "${CYAN}" "${S3_ASSET_BUCKET_BASE_NAME}" "${AWS_REGION}" "${AWS_REGION}" "${NC}"
	@printf "%bRun %b\"make <module_name>-deploy\"%b to deploy an individual module. See the README for deployment order and dependencies.%b\n" "${YELLOW}" "${CYAN}" "${YELLOW}" "${NC}"
	@printf "%bRun %b\"make deploy\"%b to deploy the entire solution in an enforced order. Note that this will take a long time and deploy many resources into your account.%b\n" "${YELLOW}" "${CYAN}" "${YELLOW}" "${NC}"

.PHONY: upload-backstage-assets-zip
upload-backstage-assets-zip:
	@aws s3api put-object \
        --bucket "${REGIONAL_ASSET_BUCKET_NAME}" \
        --key "${SOLUTION_NAME}/${SOLUTION_VERSION}/backstage.zip" \
        --body "${SOLUTION_PATH}/deployment/regional-s3-assets/backstage.zip" \
        --expected-bucket-owner "${AWS_ACCOUNT_ID}" > /dev/null
	@printf "%bFinished uploading zipped backstage assets \n%b" "${GREEN}" "${NC}"

.PHONY: verify-module
verify-module: ## Run all verifications for CMS. CAUTION: Takes a long time.
	@$(call run-module-target,verify-module,${SubMakeDirs})
	@printf "%b\nFinished verify-module.%b\n" "${GREEN}" "${NC}"

.PHONY: unit-tests
unit-tests:  ## Run unit-tests for the entire solution.
	@$(call run-module-target,unit-tests,${SubMakeDirs})
	@printf "%b\nFinished unit tests for entire solution.%b\n" "${GREEN}" "${NC}"

.PHONY: test
test:  ## Run unit-tests for the entire solution.
	@$(call run-module-target,test,${SubMakeDirs})
	@printf "%b\nFinished test for entire solution.%b\n" "${GREEN}" "${NC}"

.PHONY: update-snapshots
update-snapshots:  ## Run update-snapshots for the entire solution.
	@$(call run-module-target,update-snapshots,${SubMakeDirs})
	@printf "%b\nFinished update-snapshots.%b\n" "${GREEN}" "${NC}"

.PHONY: version
version: root-version ## Display solution name and current version and each module's version
	@process_pids=(); \
	for dir in $(SubMakeDirs); do $(MAKE) -C $$dir version & process_pids+=($$!); done; \
	for pid in $${process_pids[@]}; do wait "$${pid}"; done;

## ========================================================
## INSTALL
## ========================================================
.PHONY: root-sync
root-sync: verify-required-tools ## Using pipenv, installs python dependencies for root from Pipfile.lock.
	@printf "%bInstalling root python dependencies from Pipfile.lock.%b\n" "${MAGENTA}" "${NC}"
	@pipenv sync --quiet --python ${PYTHON_VERSION} > /dev/null
	@pipenv clean --bare --python ${PYTHON_VERSION}
	@printf "%bFinished installing root python dependencies from Pipfile.lock.%b\n" "${GREEN}" "${NC}"

.PHONY: root-lock
root-lock: verify-required-tools ## Using pipenv, upgrades root Pipfile.lock.
	@printf "%bUpdating root Pipfile.lock.%b\n" "${MAGENTA}" "${NC}"
	@pipenv lock --python ${PYTHON_VERSION} --clear > /dev/null 2>&1
	@printf "%bFinished updating root Pipfile.lock.%b\n" "${GREEN}" "${NC}"

## ========================================================
## BUILD
## ========================================================
.PHONY: asset-copy
asset-copy: ## Copy modules' build artifacts to root level folders
	@printf "%b\nBeginning asset copy.\n%b" "${GREEN}" "${NC}"
	@printf "%bCopying global assets to ${SOLUTION_PATH}/deployment%b\n" "${MAGENTA}" "${NC}"
	@rm -rf ${SOLUTION_PATH}/deployment/global-s3-assets && mkdir ${SOLUTION_PATH}/deployment/global-s3-assets
	@find source \( -name cdk.out -o -name .venv -o -name node_modules -o -name build \) -prune -false -o -name "global-s3-assets" -exec bash -c "cp -r {}/* ${SOLUTION_PATH}/deployment/global-s3-assets" \;
	@printf "%bCopying regional assets to ${SOLUTION_PATH}/deployment%b\n" "${MAGENTA}" "${NC}"
	@rm -rf ${SOLUTION_PATH}/deployment/regional-s3-assets && mkdir ${SOLUTION_PATH}/deployment/regional-s3-assets
	@find source \( -name cdk.out -o -name .venv -o -name node_modules -o -name build \) -prune -false -o -name "regional-s3-assets" -exec bash -c "cp -r {}/* ${SOLUTION_PATH}/deployment/regional-s3-assets" \;
	@printf "%bFinished asset collation.%b\n" "${GREEN}" "${NC}"

.PHONY: zip-backstage-assets
zip-backstage-assets: ## Zip backstage assets in the regional assets directory
	@printf "%b\nBeginning Backstage asset zip.\n%b" "${GREEN}" "${NC}"
	@cd ${SOLUTION_PATH}/deployment/regional-s3-assets/backstage && zip -r ${SOLUTION_PATH}/deployment/regional-s3-assets/backstage.zip . > /dev/null
	@printf "%bFinished zipping backstage assets \n%b" "${GREEN}" "${NC}"

.PHONY: build-open-source
build-open-source: ## Build open source distribution
	${SOLUTION_PATH}/deployment/build-open-source-dist.sh --solution-name ${SOLUTION_NAME}

## ========================================================
## TESTING
## ========================================================
.PHONY: pre-commit-all
pre-commit-all: ## Run pre-commit for the entire solution for all files.
	@printf "%bRunning all pre-commits.%b\n" "${MAGENTA}" "${NC}"
	pipenv run pre-commit run --all-files

## ========================================================
## UTILITY
## ========================================================
.PHONY: clean-build-artifacts
clean-build-artifacts: ## Cleans up build files, not including venvs, dependencies, or release build artifacts.
	@printf "%bRunning clean script.%b\n" "${MAGENTA}" "${NC}"
	${SOLUTION_PATH}/deployment/run-clean-build-artifacts.sh
	@printf "%bFinished clean script.%b\n" "${GREEN}" "${NC}"

.PHONY: clean-build-artifacts-release
clean-build-artifacts-release: ## Cleans up build files, including release build artifacts.
	@printf "%bRunning clean script.%b\n" "${MAGENTA}" "${NC}"
	${SOLUTION_PATH}/deployment/run-clean-build-artifacts.sh --release-build
	@printf "%bFinished clean script.%b\n" "${GREEN}" "${NC}"

.PHONY: clean-build-artifacts-pipeline
clean-build-artifacts-pipeline: ## Cleans up build files, including venvs, dependencies, and module s3 assets.
	@printf "%bRunning clean scripts.%b\n" "${MAGENTA}" "${NC}";
	${SOLUTION_PATH}/deployment/run-clean-build-artifacts.sh --dependencies --module-s3-assets
	@printf "%bFinished clean script.%b\n" "${GREEN}" "${NC}"

.PHONY: clean-build-artifacts-all
clean-build-artifacts-all: ## Cleans up existing build files, including venvs, dependencies, and release build artifacts.
	@printf "%bRunning clean script.%b\n" "${MAGENTA}" "${NC}"
	${SOLUTION_PATH}/deployment/run-clean-build-artifacts.sh --all
	@printf "%bFinished clean script.%b\n" "${GREEN}" "${NC}"

.PHONY: create-rc-file
create-rc-file: ## Create rc file for environment variables which are likely to be customized. Default values provided where able for default CMS deployment.
	@python deployment/create_rc_file.py cmsrc

.PHONY: add-ma-vars-to-rc-file
add-ma-vars-to-rc-file: ## adds envionment variables to .cmsrc required to deploy multi-account guidance stack
	@python deployment/create_rc_file.py marc

.PHONY: generate-python-requirements-files
generate-python-requirements-files: ## Generates requirements.txt files using the python binary in the .venv environments throughout the solution.
	@printf "%bGenerating requirements.txt from virtual environments (.venv) python binaries.%b\n" "${MAGENTA}" "${NC}"
	find ${SOLUTION_PATH} \( -name .venv -o -name node_modules -o -name "cdk.out" \) -prune -false -o -name "Pipfile.lock" -execdir bash -c "pipenv requirements --exclude-markers 1> requirements.txt;" \;

## ========================================================
## HELPERS
## ========================================================
.PHONY: help
help: ## Displays this help message. For a module's help, run "make <module_name>-help".
	@grep -E '^[a-zA-Z0-9 -_]+:.*##|^##.*'  ${SOLUTION_PATH}/Makefile | while read -r l; \
	do ( [[ "$$l" =~ ^"##" ]] && printf "%b%s%b\n" "${MAGENTA}" "$$(echo $$l | cut -f 2- -d' ')" "${NC}") \
	|| ( printf "%b%-35s%s%b\n" "${GREEN}" "$$(echo $$l | cut -f 1 -d':')" "$$(echo $$l | cut -f 3- -d'#')" "${NC}"); \
	done;

.PHONY: encourage
encourage: ## Sometimes we all need a little encouragement!
	@printf "%bYou can do this. Believe in yourself. :)%b\n" "${GREEN}" "${NC}"

.PHONY: root-version
root-version: ## Display solution name and current version
	@printf "%b%35.35s%b version:%b%s%b\n" "${MAGENTA}" "${SOLUTION_NAME}" "${NC}" "${GREEN}" "${SOLUTION_VERSION}" "${NC}"
