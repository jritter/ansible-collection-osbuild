#!/usr/bin/python
# Copyright: (c) 2021, Juerg Ritter <jritter@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for querying osbuild composes
"""

from composer import http_client as client
from ansible.module_utils.basic import AnsibleModule


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: compose_info

short_description: Query osbuild composes

version_added: "2.9"

description:
    - "This module can be used to query osbuild composes"

options:
    status:
        description:
            - Filter for states, can be all, running, finished, queued or failed
        required: false
        choices: ["all", "running", "finished", "queued", "failed"]
        type: str
        default: "all"
    id:
        description:
            - Specifies the ID of a specific compose to get detailed information
        required: false
        type: str

author:
    - Juerg Ritter (@juergritter)
'''

EXAMPLES = '''
# Get all composes
- name: get all osbuild composes
  jritter.osbuild.compose_info:
  register: composes

- name: show composes
  debug:
    var: composes

# Get all finished composes
- name: get finished osbuild composes
  jritter.osbuild.compose_info:
    status: finished
  register: composes

- name: show composes
  debug:
    var: composes

# Get detailed information of compose 19ea67c1-39d7-4b81-8690-2c89f10b3e9a
- name: get detail info of compose
  jritter.osbuild.compose_info:
    id: 19ea67c1-39d7-4b81-8690-2c89f10b3e9a
  register: compose

- name: show compose
  debug:
    var: compose
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
        status=dict(type='str', required=False, default='all'),
        id=dict(type='str', required=False)
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

    if module.params['id']:
        ret = client.get_url_json(SOCKET, '/api/v1/compose/info/' + module.params['id'])
        if 'errors' in ret.keys():
            result['failed'] = True
    else:
        ret = []
        if module.params['status'] == 'all' or module.params['status'] == 'running':
            ret += client.get_url_json(SOCKET, '/api/v1/compose/queue')['run']
        if module.params['status'] == 'all' or module.params['status'] == 'waiting':
            ret += client.get_url_json(SOCKET, '/api/v1/compose/queue')['new']
        if module.params['status'] == 'all' or module.params['status'] == 'finished':
            ret += client.get_url_json(SOCKET, '/api/v1/compose/finished')['finished']
        if module.params['status'] == 'all' or module.params['status'] == 'failed':
            ret += client.get_url_json(SOCKET, '/api/v1/compose/failed')['failed']

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
