SHELL := bash
.PHONY: vendor clean

HCLOUD_URL = https://github.com/hetznercloud/hcloud-python
HCLOUD_VERSION = main
HCLOUD_VENDOR = plugins/module_utils/vendor/hcloud

vendor:
	git clone --depth=1 --branch=$(HCLOUD_VERSION) $(HCLOUD_URL) hcloud-python

	rm -Rf $(HCLOUD_VENDOR)
	mv hcloud-python/hcloud $(HCLOUD_VENDOR)
	python3 scripts/vendor.py $(HCLOUD_VENDOR)

	rm -Rf hcloud-python

clean:
	git clean -xdf \
		-e tests/integration/cloud-config-hcloud.ini
