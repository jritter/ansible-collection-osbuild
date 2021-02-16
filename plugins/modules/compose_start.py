#!/usr/bin/python
# Copyright: (c) 2021, Juerg Ritter <jritter@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for starting an osbuild
"""

from composer import http_client as client
from ansible.module_utils.basic import AnsibleModule
import json


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: compose_start

short_description: Start osbuild composes

version_added: "2.9"

description:
    - "This module can be used to start osbuild composes"

options:
    blueprint_name:
        description:
            - Blueprint which will be used for image creation
        required: true
        type: str
    compose_type:
        description:
            - Specifies the type of the image which should be built (e.g. openstack, qcow2, rhel-edge-commit, etc.).
            - Invoke ´composer-cli compose types´ for all types
        required: true
        type: str
    ref: 
        description:
            - "Applicable only for ostree based builds (fedora-iot-commit, rhel-edge-commit): Speci fies the ostree ref."
        required: false
        type: str
        default: "rhel/8/x86_64/edge"
    parent:
        description:
            - "Applicable only for ostree based builds (fedora-iot-commit, rhel-edge-commit): Specifies the parent commit of the build."
        type: str
        required: false
        default: ""

author:
    - "Juerg Ritter (@juergritter)"

'''

EXAMPLES = '''
# Start ostree compose
- name: start osbuild compose
  jritter.osbuild.compose_start:
    blueprint_name: myblueprint
    compose_type: rhel-edge-commit
  register: compose

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
        blueprint_name=dict(type='str', required=True),
        compose_type=dict(type='str', required=True),
        ref=dict(type='str', required=False, default='rhel/8/x86_64/edge'),
        parent=dict(type='str', required=False, default=''),
    )

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
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    compose_params = {
        'blueprint_name': module.params['blueprint_name'],
        'compose_type': module.params['compose_type'],
        'ref': module.params['ref'],
        'parent': module.params['parent']
    }
    ret = client.post_url_json(SOCKET, '/api/v1/compose', json.dumps(compose_params))
    result['ansible_module_results'] = ret

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    """main
    """
    run_module()

if __name__ == '__main__':
    main()
