SHELL := bash
.PHONY: vendor clean

vendor:
	python3 scripts/vendor.py

vendor-check:
	python3 scripts/vendor.py --check

venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

lint: venv
	venv/bin/pylint plugins

lint-docs: venv
	venv/bin/antsibull-docs lint-collection-docs \
		--plugin-docs \
		--validate-collection-refs self \
		--skip-rstcheck \
		.

clean:
	git clean -xdf \
		-e tests/integration/cloud-config-hcloud.ini
