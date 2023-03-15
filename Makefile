# This Makefile is designed for testing purposes only!
# It expects that NSO has been installed and $NCS_DIR/ncsrc is activated.
# You need to define NSO_RUN_DIR environment variable pointing to the NSO running directory.
NCS_RUN_DIR ?= ${CURDIR}/test-oc-services
DIR = ${CURDIR}

all:
	$(MAKE) -C packages/mdd/src all
	$(MAKE) -C packages/oc-service-discovery/src all
.PHONY: all

clean:
	$(MAKE) -C packages/mdd/src clean
	$(MAKE) -C packages/oc-service-discovery/src clean
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
#	ln -sf /Users/ygorelik/neds/cisco-ios-cli-6.83 packages/cisco-ios-cli-6.83
#	-ncs-netsim create-device packages/cisco-ios-cli-6.83 xe
#	-ncs-netsim ncs-xml-init xe > ncs-cdb/xe-ncs-xml-init.xml
.PHONY: test-setup

test-reset:
	cd ${NCS_RUN_DIR}; ncs-setup --reset
.PHONY: test-reset

cli:
	ncs_cli -Cu admin
.PHONY: cli
