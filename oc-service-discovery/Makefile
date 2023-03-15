all:
	$(MAKE) -C src all

clean:
	$(MAKE) -C src clean

setup:
	cp ../package_nso_to_oc/common.py python/package_nso_to_oc/
	cp -R ../package_nso_to_oc/xe python/package_nso_to_oc/
	cp -R ../package_nso_to_oc/xr python/package_nso_to_oc/

reset:
	rm -rf python/nso_to_oc/*
