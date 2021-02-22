#!/usr/bin/python
# Copyright: (c) 2021, Juerg Ritter <jritter@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for managing osbuild blueprints
"""

from composer import http_client as client
from ansible.module_utils.basic import AnsibleModule

import pytoml as toml

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: blueprint

short_description: Manages osbuild blueprints

version_added: "2.9"

description:
    - "This module can be used to manage osbuild blueprints"

options:
    name:
        description:
            - Name of the blueprint
            - name can be used in combination with state: absent to reference a blueprint that must not exist
            - mutually exclusive with C(definition)
        type: str
    definition:
        description:
            - definition of the blueprint in TOML format
            - mutually exclusive with C(name)
        type: str
    state:
        description:
            - Defines whether the blueprint is present or absent
        choices: ["present", "absent"]

author:
    - "Juerg Ritter (@juergritter)"

'''

EXAMPLES = '''
# Start ostree compose
- name: define a blueprint
  jritter.osbuild.blueprint:
    definition: lookup('file', 'files/myblueprint.toml')
    state: present
  register: blueprint

- name: define a blueprint as absent
  jritter.osbuild.blueprint:
    name: myblueprint
    state: absent

'''

RETURN = '''
results:
    description: List of all the matching composes
    type: str
    returned: always
'''

SOCKET = '/run/weldr/api.socket'

def run_module():
    """Module main function
    """
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=False),
        definition=dict(type='str', required=False),
        state=dict(type='str', required=False, default='present'),
    )

    mutually_exclusive = [
        ('name', 'definition')
    ]

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        ansible_module_results=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # Figure out the name of the blueprint, either from the name or the TOML definition
    if module.params['name']:
        blueprint_name = module.params['name']
    else:
        blueprint_name = toml.loads(module.params['definition'])['name']

    result['blueprint_name'] = blueprint_name

    # See what is already present

    blueprint_present = True
    try:
        available_blueprint = client.get_url_raw(SOCKET, '/api/v1/blueprints/info/' +
                                                 blueprint_name + '?format=toml')
    except RuntimeError:
        # The composer.http_client throws a Runtime Error if the API returns 400
        blueprint_present = False


    if module.params['state'] == 'present' and not blueprint_present:
        result['ansible_module_results'] = client.post_url_toml(SOCKET,
                '/api/v1/blueprints/new', module.params['definition'])
        result['ansible_module_results']['definition'] = client.get_url_raw(SOCKET,
                '/api/v1/blueprints/info/' + blueprint_name + '?format=toml')
        result['changed'] = True
    elif module.params['state'] == 'present' \
        and blueprint_present \
        and available_blueprint != module.params['definition']:
        result['ansible_module_results'] = client.post_url_toml(SOCKET,
                '/api/v1/blueprints/new', module.params['definition'])
        result['ansible_module_results']['definition'] = client.get_url_raw(SOCKET,
                '/api/v1/blueprints/info/' + blueprint_name + '?format=toml')
        result['changed'] = True
    elif module.params['state'] == 'absent' and blueprint_present:
        result['ansible_module_results'] = client.delete_url_json(SOCKET,
                '/api/v1/blueprints/delete/' + blueprint_name)
        result['changed'] = True
    else:
        result['ansible_module_results']['definition'] = client.get_url_raw(SOCKET,
                '/api/v1/blueprints/info/' + blueprint_name + '?format=toml')
        result['changed'] = False


    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    """main
    """
    run_module()

if __name__ == '__main__':
    main()
