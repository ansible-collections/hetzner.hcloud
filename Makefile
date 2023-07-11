SHELL := bash
.PHONY: vendor clean

vendor:
	python3 scripts/vendor.py

clean:
	git clean -xdf \
		-e tests/integration/cloud-config-hcloud.ini
