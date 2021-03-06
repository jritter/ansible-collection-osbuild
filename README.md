# Ansible Collection - jritter.osbuild

This collection provides a set of modules in order to interact with the osbuild composer API. It is designed with the composer-cli tool in mind. The module uses the same python client module. The communication goes through the Weldr UNIX Socket REST API. The modules can be used in place of the composer-cli tool, or the cockpit-composer Plugin for Cockpit.

## Disclaimer

This collection is in a very early stage of development. It has only been tested using Ansible 2.9 on a Red Hat Enterprise Linux 8 image builder host. Feel free to create a ticket on GitHub in case of comments and problems:

https://github.com/jritter/ansible-collection-osbuild/issues


## Installation

The collection can be installed using the following command:

```
$ ansible-galaxy collection install jritter.osbuild
```

## Prerequisites

The Ansible target node must have osbuild-composer and composer-cli installed.

## Example Blueprint

```
$ cat files/myblueprint.toml
name = "myblueprint"
description = "My Blueprint"
version = "0.0.1"
modules = []
groups = []

[[packages]]
name = "curl"
version = "*"

[[packages]]
name = "podman"
version = "*"

```

## Example Playbook


```yaml
- name: osbuild collection example playbook
  hosts: control  # The playbook has to target hosts with osbuild-composer installed
  gather_facts: no # you can if you want to, but not necessary
  become: yes # we need read/write access to /run/weldr/api.socket
  tasks:
  
  # Here we can define a new blueprint, which can be loaded
  # from the control node using the file lookup module
  #
  # works the same way as the following command:
  # $ composer-cli blueprints push files/myblueprint.toml 
  - name: Define a blueprint
    jritter.osbuild.blueprint:
      definition: "{{ lookup('file', 'files/myblueprint.toml') }}"
      state: present
  
  # Here we start a compose of type rhel-edge-commit,
  # using the blueprint we created above
  # By specifying wait: yes, the module will block until
  # the build has finished of (hopefully not) failed
  #
  # works the same way as the following command:
  # $ composer-cli compose start myblueprint rhel-edge-commit
  - name: start osbuild compose
    jritter.osbuild.compose_start:
      blueprint_name: myblueprint
      compose_type: rhel-edge-commit
      wait: yes
    register: compose

  - name: Print finished compose
    debug:
      var: compose

  # Downloads the finished compose into the /tmp
  # directory of the target node
  #
  # $ composer-cli compose image <build-id>
  - name: Download compose to target node
    jritter.osbuild.compose_image:
      id: "{{ compose.ansible_module_results.id }}"
      dest: /tmp
    register: compose_download

  - name: Print info of downloaded image
    debug:
      var: compose_download

  # Lists all the available composes on the
  # target node
  #
  # $ composer-cli compose list
  - name: Get all osbuild composes
    jritter.osbuild.compose_info:
      status: all
    register: composes

  - name: Show composes
    debug:
      var: composes

```


## References

- https://github.com/osbuild/osbuild-composer
- https://www.osbuild.org/
