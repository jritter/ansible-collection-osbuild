#!/usr/bin/python
# Copyright: (c) 2021, Juerg Ritter <jritter@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible Module for downloading an image built with osbuild
"""

import os
import json

from ansible.module_utils.basic import AnsibleModule
from composer import http_client as client
from composer.unix_socket import UnixHTTPConnectionPool

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: compose_image

short_description: Downloads compose images

version_added: "2.9"

description:
    - "This module can be used to download images created by osbuild-composer"

options:
    id:
        description:
            - Specifies the ID of the Image that should be downloaded.
        required: true
    dest:
        description:
            - Specifies the path where the downloaded image should be saved. 
            - If the path is the directory, the filename will be defined as returned by the composer API. 
            - If a filename is specified, the image will be written to this file.
        required: true

author:
    - Juerg Ritter (@juergritter)
'''

EXAMPLES = '''
# Download Image
- name: start osbuild compose
  jritter.osbuild.compose_image:
    id: 54ee98a4-d83b-4907-b656-dde0429b00bd
    dest: /tmp/
'''

RETURN = '''
ansible_module_results:
    status: HTTP status code of the API
    dest: Filename of the 
    returned: always
'''

SOCKET = '/run/weldr/api.socket'

def run_module():
    """Module main function
    """
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        id=dict(type='str', required=True),
        dest=dict(type='str', required=True)
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

    http = UnixHTTPConnectionPool(SOCKET)
    response = http.request("GET", '/api/v1/compose/image/'
                            + module.params['id'], preload_content=False)
    if response.status == 400:
        err = json.loads(response.data.decode("utf-8"))
        if not err["status"]:
            msgs = [e["msg"] for e in err["errors"]]
            raise RuntimeError(", ".join(msgs))

    downloadpath = module.params['dest']

    if os.path.isdir(downloadpath):
        downloadpath = os.path.join(downloadpath, client.get_filename(response.headers))

    with open(downloadpath, "wb") as image_file:
        while True:
            data = response.read(10 * 1024**2)
            if not data:
                break
            image_file.write(data)

    result['ansible_module_results'] = {
        'dest': downloadpath,
        'status': response.status
    }
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    """main
    """
    run_module()

if __name__ == '__main__':
    main()
