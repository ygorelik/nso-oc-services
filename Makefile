# This Makefile is designed for testing purposes only!
# It expects that NSO has been installed and $NCS_DIR/ncsrc is activated.
# You need to define NSO_RUN_DIR environment variable pointing to the NSO running directory;
# absolute path is required.
#
# Before starting/restarting the NSO make sure these environment variables are set:
# - NSO_URL - URL for the NSO server, ex.: http://localhost:443
# - NSO_USERNAME - default: admin
# - NSO_PASSWORD - default: admin

NCS_RUN_DIR ?= ${CURDIR}/test-oc-services
DIR = ${CURDIR}

all:
	$(MAKE) -C mdd/src all
	$(MAKE) -C oc-service-discovery/src all
.PHONY: all

clean:
	$(MAKE) -C mdd/src clean
	$(MAKE) -C oc-service-discovery/src clean
.PHONY: clean

stop:
	-cd ${NCS_RUN_DIR}; ncs --stop; ncs-netsim stop
.PHONY: stop

start:
	cd ${NCS_RUN_DIR}; ncs-netsim start; ncs
.PHONY: start

setup:
	cd ${NCS_RUN_DIR}; ln -sf ${DIR}/package_nso_to_oc
	cd ${NCS_RUN_DIR}/packages; ln -sf ${DIR}/mdd; ln -sf ${DIR}/oc-service-discovery
.PHONY: setup

test-setup:
	mkdir -p ${NCS_RUN_DIR}
	ncs-setup --dest ${NCS_RUN_DIR}
	cd ${NCS_RUN_DIR}; ln -sf ${DIR}/package_nso_to_oc
	cd ${NCS_RUN_DIR}/packages; ln -sf ${DIR}/mdd; ln -sf ${DIR}/oc-service-discovery
	cd ${NCS_RUN_DIR}/packages; ln -sf /Users/ygorelik/nso-6.0.4/packages/neds/cisco-ios-cli-6.92
	mkdir -p ${NCS_RUN_DIR}/netsim
	cd ${NCS_RUN_DIR}; ncs-netsim create-device packages/cisco-ios-cli-6.92 xe
	cd ${NCS_RUN_DIR}; ncs-netsim ncs-xml-init xe > ncs-cdb/xe-ncs-xml-init.xml
.PHONY: test-setup

test-reset:
	cd ${NCS_RUN_DIR}; ncs-setup --reset
.PHONY: test-reset

cli:
	ncs_cli -Cu admin
.PHONY: cli
