==============================================
Hetzner Cloud Ansible Collection Release Notes
==============================================

.. contents:: Topics

v1.6.0
======

Minor Changes
-------------

- hcloud_rdns Add support for load balancer

v1.5.0
======

Major Changes
-------------

- Introduction of placement groups

Minor Changes
-------------

- hcloud_firewall Add description field to firewall rules

Bugfixes
--------

- hcloud_rdns improve error message on not existing server/Floating IP
- hcloud_server backups property defaults to None now instead of False

v1.4.4
======

Bugfixes
--------

- hcloud_server Improve Error Message when attaching a not existing firewall to a server
- hcloud_volume Force detaching of volumes on servers before deletion

v1.4.3
======

Bugfixes
--------

- hcloud_server Fix incompatbility with python < 3.6
- hcloud_server Improve error handling when using not existing server types

v1.4.2
======

Bugfixes
--------

- inventory fix image name was set as server type instead of the correct server type

v1.4.1
======

Minor Changes
-------------

- hcloud_server - improve the handling of deprecated images
- hcloud_server - improve the validation and error response for not existing images
- inventory - support jinjia templating within `token`

v1.4.0
======

Security Fixes
--------------

- hcloud_certificate - mark the ``private_key`` parameter as ``no_log`` to prevent potential leaking of secret values (https://github.com/ansible-collections/hetzner.hcloud/pull/70).

Bugfixes
--------

- hcloud_firewall - fix idempotence related to rules comparison (https://github.com/ansible-collections/hetzner.hcloud/pull/71).
- hcloud_load_balancer_service - fix imported wrong HealthCheck from hcloud-python (https://github.com/ansible-collections/hetzner.hcloud/pull/73).
- hcloud_server - fix idempotence related to firewall handling (https://github.com/ansible-collections/hetzner.hcloud/pull/71).

v1.3.1
======

Bugfixes
--------

- hcloud_server - fix a crash related to check mode if ``state=started`` or ``state=stopped`` (https://github.com/ansible-collections/hetzner.hcloud/issues/54).

v1.3.0
======

Minor Changes
-------------

- Add firewalls to hcloud_server module

New Modules
-----------

- hcloud_firewall - Manage Hetzner Cloud Firewalls

v1.2.1
======

Bugfixes
--------

- Inventory Restore Python 2.7 compatibility

v1.2.0
======

Minor Changes
-------------

- Dynamic Inventory Add option to specifiy the token_env variable which is used for identification if now token is set
- Improve imports of API Exception
- hcloud_server_network Allow updating alias ips
- hcloud_subnetwork Allow creating vswitch subnetworks

New Modules
-----------

- hcloud_load_balancer_info - Gather infos about your Hetzner Cloud load_balancers.

v1.1.0
======

Minor Changes
-------------

- hcloud_floating_ip Allow creating Floating IP with protection
- hcloud_load_balancer Allow creating Load Balancer with protection
- hcloud_network Allow creating Network with protection
- hcloud_server Allow creating server with protection
- hcloud_volume Allow creating Volumes with protection

Bugfixes
--------

- hcloud_floating_ip Fix idempotency when floating ip is assigned to server

v1.0.0
======

Minor Changes
-------------

- hcloud_load_balancer Allow changing the type of a Load Balancer
- hcloud_server Allow the creation of servers with enabled backups

v0.2.0
======

Bugfixes
--------

- hcloud inventory plugin - Allow usage of hcloud.yml and hcloud.yaml - this was removed by error within the migration from build-in ansible to our collection

v0.1.0
======

New Modules
-----------

- hcloud_floating_ip - Create and manage cloud Floating IPs on the Hetzner Cloud.
- hcloud_load_balancer - Create and manage cloud Load Balancers on the Hetzner Cloud.
- hcloud_load_balancer_network - Manage the relationship between Hetzner Cloud Networks and Load Balancers
- hcloud_load_balancer_service - Create and manage the services of cloud Load Balancers on the Hetzner Cloud.
- hcloud_load_balancer_target - Manage Hetzner Cloud Load Balancer targets
- hcloud_load_balancer_type_info - Gather infos about the Hetzner Cloud Load Balancer types.
