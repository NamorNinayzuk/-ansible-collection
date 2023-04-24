#!/usr/bin/python3

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: yc
short_description: Yandex Cloud networks controller
version_added: "1.0.1"
description: This module translate commands to Yandex Cloud CLI in order to control networks
options:
    net:
        description: name of the network
        required: true
        type: str
    subnet:
        description: name of the subnet
        required: true
        type: str
    ip_range:
        description: IP address space allocated to subnet in CIDR notation
        required: false
        type: str
        default: '10.2.0.0/16'
    state:
        description: state of subnet/net - 'exists' or 'absent'
        required: false
        type: str
        default: 'exists'
extends_documentation_fragment:
    - test.utils.yc
'''

EXAMPLES = r'''
- name: Create YC virtual networks
  artem_shtepa.utils.yc_vpc:
    net: my_net
    subnet: my_subnet
- name: Destroy YC virtual networks
  artem_shtepa.utils.yc_vpc:
    net: my_net
    subnet: my_subnet
    state: absent
'''

RETURN = r'''
version:
    description: Yandex.Cloud CLI version
    type: str
    returned: always
    sample: 'Yandex Cloud CLI 0.93.0 linux/amd64'
net_config:
    description: Network configuration from Yandex Cloud
    returned: if net exists or created
subnet_config:
    description: Subnet configuration of network from Yandex Cloud
    returned: if subnet exists or created
'''

from ansible.module_utils.basic import AnsibleModule
import os, subprocess, json

def get_oneline_param(cmd):
    p = subprocess.run(cmd, capture_output=True, encoding='utf-8', shell=True)
    return int(p.returncode), str(p.stdout.replace('\n','')), str(p.stderr)

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        net=dict(type='str', required=True),
        subnet=dict(type='str', required=True),
        ip_range=dict(type='str', required=False, default='10.2.0.0/16'),
        state=dict(type='str', required=False, default='exists', choices=['exists','absent'])
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    #Check YC CLI availability
    res = get_oneline_param('yc --version')
    if res[0] != 0:
        module.fail_json(msg='Can`t run YandexCloud CLI. Check https://cloud.yandex.ru/docs/cli/operations/install-cli', **result)
    else:
        result['version'] = res[1]

    #Verify YC CLI authorizaion
    for param in ['token', 'cloud-id', 'folder-id', 'compute-default-zone']:
        res = get_oneline_param('yc config get '+param)
        if res[0] != 0:
            module.fail_json(msg='Can`t get config param `'+param+'`. Check YC CLI authorization by `yc init`', **result)

    create_subnet = False

    #Check net availability
    res = get_oneline_param('yc vpc net get '+module.params['net']+ ' --format=json-rest')
    if res[0] != 0:
        # Net not found
        if module.params['state'] == 'absent':
            # Nothing to do
            module.exit_json(**result)
        else:
            # Create new net
            res = get_oneline_param('yc vpc net create '+module.params['net']+' --format=json-rest')
            if res[0] != 0:
                module.fail_json(msg='Can`t create network: '+res[2], **result)
            result['net_config'] = json.loads(res[1])
            create_subnet = True
            result['changed'] = True
    else:
        # Net is found
        if module.params['state'] == 'absent':
            # Try to destroy subnet
            res = get_oneline_param('yc vpc subnet delete '+module.params['subnet'])
            if res[0] != 0:
                module.fail_json(msg='Can`t delete subnet: '+res[2], **result)
            # Destroy net
            res = get_oneline_param('yc vpc net delete '+module.params['net'])
            if res[0] != 0:
                module.fail_json(msg='Can`t delete net: '+res[2], **result)
            result['changed'] = True
        else:
            result['net_config'] = json.loads(res[1])
            create_subnet = True

    #Check subnet availability
    if create_subnet:
        res = get_oneline_param('yc vpc subnet get '+module.params['subnet']+' --format=json-rest')
        if res[0] != 0:
            # Subnet not exists
            res = get_oneline_param('yc vpc subnet create '+module.params['subnet']+' --network-name '+module.params['net']+' --range '+module.params['ip_range']+' --format=json-rest')
            if res[0] != 0:
                module.fail_json(msg='Can`t create subnet: '+res[2], **result)
            result['changed'] = True
        result['subnet_config'] = json.loads(res[1])


    # successful module execution
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
