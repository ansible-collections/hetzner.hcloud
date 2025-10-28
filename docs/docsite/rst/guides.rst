.. _ansible_collections.hetzner.hcloud.docsite.authentication:

Authentication
==============

To `authenticate the API call against the Hetzner Cloud API <https://docs.hetzner.cloud/reference/cloud#authentication>`_ when
using the ``hetzner.hcloud`` collection, you can provide the API token by different means:

You can pass the API token using an environment variable (recommended):

.. code-block:: bash

    export HCLOUD_TOKEN='LRK9DAWQ1ZAEFSrCNEEzLCUwhYX1U3g7wMg4dTlkkDC96fyDuyJ39nVbVjCKSDfj'

    # Verify that your token is working
    ansible -m hetzner.hcloud.location_info localhost

Alternatively, you may provide the API token directly as module argument:

.. code-block:: yaml

    - name: Create server
      hetzner.hcloud.server:
        api_token: LRK9DAWQ1ZAEFSrCNEEzLCUwhYX1U3g7wMg4dTlkkDC96fyDuyJ39nVbVjCKSDfj
        name: my-server
        server_type: cpx22
        image: debian-12
        state: present

To reduce the duplication of the above solution, you may configure the
``hetzner.hcloud.*`` modules using the ``hetzner.hcloud.all`` action group, for
example if you want to store your API token in a vault:

.. code-block:: yaml

    - name: Demonstrate the usage of the 'hetzner.hcloud.all' module_defaults group
      hosts: localhost
      connection: local

      module_defaults:
        group/hetzner.hcloud.all:
          api_token: "{{ _vault_hcloud_api_token }}"

      tasks:
        - name: Create server
          hetzner.hcloud.server:
            name: my-server
            server_type: cpx22
            image: debian-12
            state: present

Experimental features
=====================

Experimental features are published as part of our regular releases (e.g. a product
public beta). During an experimental phase, breaking changes on those features may occur
within minor releases.

The stability of experimental features is not related to the stability of its upstream API.

Experimental features have different levels of maturity (e.g. experimental, alpha, beta)
based on the maturity of the upstream API.

While experimental features will be announced in the release notes, you can also find
whether a module, or filter is experimental in its documentation:

.. code-block:: txt

    Experimental: $PRODUCT is $MATURITY, breaking changes may occur within minor releases. See https://docs.hetzner.cloud/changelog#$SLUG for more details.
