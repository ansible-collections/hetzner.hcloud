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
        server_type: cx11
        image: debian-12
        state: present
