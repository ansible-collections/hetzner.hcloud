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

docs-lint:
	venv/bin/antsibull-docs lint-collection-docs --plugin-docs .

clean:
	git clean -xdf \
		-e tests/integration/cloud-config-hcloud.ini
