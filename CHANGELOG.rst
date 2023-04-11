==============================================
Hetzner Cloud Ansible Collection Release Notes
==============================================

.. contents:: Topics


v1.11.0
=======

Minor Changes
-------------

- hcloud_image_info - Add cpu architecture field to return value.
- hcloud_image_info - Allow filtering images by cpu architecture.
- hcloud_server - Select matching image for the cpu architecture of the server type on create & rebuild.
- hcloud_server_type_info - Add cpu architecture field to return value.
- inventory plugin - Add cpu architecture to server variables.

v1.10.1
=======

Bugfixes
--------

- hcloud_server - Prevent backups from being disabled when undefined
- hcloud_server - Server locked after attaching to placement group

v1.10.0
=======

Minor Changes
-------------

- hcloud_server - add private_networks_info containing name and private ip in responses
- hcloud_server_info - add private_networks_info containing name and private ip in responses
- inventory plugin - Add list of all private networks to server variables.
- inventory plugin - Add new connect_with setting public_ipv6 to connect to discovered servers via public IPv6 address.
- inventory plugin - Add public IPv6 address to server variables.
- inventory plugin - Log warning instead of crashing when some servers do not work with global connect_with setting.

Breaking Changes / Porting Guide
--------------------------------

- inventory plugin - Python v3.5+ is now required.

v1.9.1
======

Bugfixes
--------

- hcloud_server - externally attached networks (using hcloud_server_network) were removed when not specified in the hcloud_server resource

v1.9.0
======

Minor Changes
-------------

- dynamic inventory - add support changing the name of the top level group all servers are added to
- hcloud_firewall - add support for esp and gre protocols

Bugfixes
--------

- hcloud_firewall - the deletion could fail if the firewall was referenced right before
- hcloud_server - fix backup window was given out as "None" instead of null
- hcloud_server_info - fix backup window was given out as "None" instead of null
- hcloud_volume - fix server name was given out as "None" instead of null if no server was attached
- hcloud_volume_info - fix server name was given out as "None" instead of null if no server was attached

v1.8.2
======

Bugfixes
--------

- dynamic inventory - fix crash when having servers without IPs (flexible networks)
- hcloud_server - When state stopped and server is created, do not start the server
- hcloud_server_info - fix crash when having servers without IPs (flexible networks)

v1.8.1
======

v1.8.0
======

New Modules
-----------

Hetzner
~~~~~~~

hcloud
^^^^^^

- hetzner.hcloud.hcloud_primary_ip - Create and manage cloud Primary IPs on the Hetzner Cloud.

v1.7.1
======

Minor Changes
-------------

- inventory - allow filtering by server status

Bugfixes
--------

- hcloud_server_network - fixes changed alias_ips by using sorted

v1.7.0
======

Minor Changes
-------------

- inventory - support jinjia templating within `network`

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
