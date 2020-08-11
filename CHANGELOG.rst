==============================================
Hetzner Cloud Ansible Collection Release Notes
==============================================

.. contents:: Topics


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
