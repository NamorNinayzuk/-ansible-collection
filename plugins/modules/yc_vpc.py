#!/usr/bin/python3

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os, subprocess, json

def get_oneline_param(cmd):
    p = subprocess.run(cmd, capture_output=True, encoding='utf-8', shell=True)
    return int(p.returncode), str(p.stdout.replace('\n','')), str(p.stderr)

def run_module():
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

    res = get_oneline_param('yc --version')
    if res[0] != 0:
        module.fail_json(msg='Can`t run YandexCloud CLI. Check https://cloud.yandex.ru/docs/cli/operations/install-cli', **result)
    else:
        result['version'] = res[1]

    for param in ['token', 'cloud-id', 'folder-id', 'compute-default-zone']:
        res = get_oneline_param('yc config get '+param)
        if res[0] != 0:
            module.fail_json(msg='Can`t get config param `'+param+'`. Check YC CLI authorization by `yc init`', **result)

    create_subnet = False

    res = get_oneline_param('yc vpc net get '+module.params['net']+ ' --format=json-rest')
    if res[0] != 0:
        if module.params['state'] == 'absent':
            module.exit_json(**result)
        else:
            res = get_oneline_param('yc vpc net create '+module.params['net']+' --format=json-rest')
            if res[0] != 0:
                module.fail_json(msg='Can`t create network: '+res[2], **result)
            result['net_config'] = json.loads(res[1])
            create_subnet = True
            result['changed'] = True
    else:
        if module.params['state'] == 'absent':
            res = get_oneline_param('yc vpc subnet delete '+module.params['subnet'])
            if res[0] != 0:
                module.fail_json(msg='Can`t delete subnet: '+res[2], **result)
            res = get_oneline_param('yc vpc net delete '+module.params['net'])
            if res[0] != 0:
                module.fail_json(msg='Can`t delete net: '+res[2], **result)
            result['changed'] = True
        else:
            result['net_config'] = json.loads(res[1])
            create_subnet = True

    if create_subnet:
        res = get_oneline_param('yc vpc subnet get '+module.params['subnet']+' --format=json-rest')
        if res[0] != 0:
            # Subnet not exists
            res = get_oneline_param('yc vpc subnet create '+module.params['subnet']+' --network-name '+module.params['net']+' --range '+module.params['ip_range']+' --format=json-rest')
            if res[0] != 0:
                module.fail_json(msg='Can`t create subnet: '+res[2], **result)
            result['changed'] = True
        result['subnet_config'] = json.loads(res[1])

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
