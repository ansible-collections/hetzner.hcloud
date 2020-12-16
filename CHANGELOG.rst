==============================================
Hetzner Cloud Ansible Collection Release Notes
==============================================

.. contents:: Topics

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
