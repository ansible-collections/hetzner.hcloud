.. _ansible_collections.hetzner.hcloud.docsite.authentication:

Authentication
==============

To `authenticate the API call against the Hetzner Cloud API <https://docs.hetzner.cloud/#authentication>`_ when
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
        server_type: cx22
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
            server_type: cx22
            image: debian-12
            state: present
