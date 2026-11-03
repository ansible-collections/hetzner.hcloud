SHELL := bash
.PHONY: vendor clean dev

dev:
	if [[ -f .env ]]; then set -a; source .env; set +a; fi; \
	cat tests/integration/cloud-config-hcloud.ini.in | envsubst | tee tests/integration/cloud-config-hcloud.ini; \
	cat tests/integration/integration_config.yml.in | envsubst | tee tests/integration/integration_config.yml;

vendor:
	python3 scripts/vendor.py

vendor-check:
	python3 scripts/vendor.py --check

venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt -r requirements-dev.txt

lint: venv
	venv/bin/pylint plugins

lint-docs: venv
	venv/bin/antsibull-docs lint-collection-docs \
		--plugin-docs \
		--validate-collection-refs self \
		--check-extra-docs-refs \
		.

clean:
	git clean -xdf -e .env*

sanity:
	ansible-test sanity --color --truncate 0 -v \
		--exclude plugins/module_utils/_vendor/ \
		--exclude scripts/ \
		--exclude tests/utils/ \
		--docker default \
		--allow-disabled

units:
	ansible-test units --color --truncate 0 -v \
		--docker default

integration:
	ansible-test integration --color --truncate 0 -v \
		--docker default \
		--allow-disabled
