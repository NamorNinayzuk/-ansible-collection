#!/usr/bin/python3


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os, subprocess, json


update_allowed = ['cores','core-fraction','memory']


def get_oneline_param(cmd):
    p = subprocess.run(cmd, capture_output=True, encoding='utf-8', shell=True)
    return int(p.returncode), str(p.stdout.replace('\n','')), str(p.stderr)


def build_cmd_line(params):
    cmd = ''
    for p in params:
        buf = ''
        v = params[p]
        if type(v) == bool:
            if v != True:
                p = ''
        elif type(v) == dict:
            for p2 in v:
                if buf != '':
                    buf += ','
                if v[p2].find(' ') >= 0:
                    buf += p2+'="'+v[p2]+'"'
                else:
                    buf += p2+'='+v[p2]
        else:
            buf = str(v)
        if p != '':
            if cmd != '':
                cmd += ' '
            cmd += '--'+str(p)
            if buf != '':
                cmd += ' '+buf
    return cmd


def run_module():
    module_args = dict(
        machine=dict(type='str', required=True),
        config=dict(type='dict', required=False, default=dict()),
        state=dict(type='str', required=False, default='exists', choices=['exists','absent'])
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    yc_auth = dict()

    res = get_oneline_param('yc --version')
    if res[0] != 0:
        module.fail_json(msg='Can`t run YandexCloud CLI. Check https://cloud.yandex.ru/docs/cli/operations/install-cli', **result)
    else:
        result['version'] = res[1]

    for param in ['token', 'cloud-id', 'folder-id', 'compute-default-zone']:
        res = get_oneline_param('yc config get '+param)
        if res[0] != 0:
            module.fail_json(msg='Can`t get config param `'+param+'`. Check YC CLI authorization by `yc init`', **result)
        else:
            yc_auth[param] = res[1]

    if not 'zone' in module.params['config']:
        module.params['config']['zone'] = yc_auth['compute-default-zone']

    res = get_oneline_param('yc compute instance get '+module.params['machine']+' --format=json')
    if res[0] != 0:
        if module.params['state'] == 'absent':
            module.exit_json(**result)
        else:
            result['yc_args'] = build_cmd_line(module.params['config'])
            res = get_oneline_param('yc compute instance create '+module.params['machine']+' '+build_cmd_line(module.params['config'])+' --format=json')
            if res[0] != 0:
                module.fail_json(msg=res[2], **result)
            result['config'] = json.loads(res[1])
            result['changed'] = True
    else:
        result['config'] = json.loads(res[1])
        if module.params['state'] == 'absent':
            res = get_oneline_param('yc compute instance delete '+module.params['machine'])
            if res[0] != 0:
                module.fail_json(msg=res[2], **result)
            result['changed'] = True
        else:
            upd_params = dict()
            for p in update_allowed:
                if p in module.params['config']:
                    upd_params[p] = module.params['config'][p]
            need_update = False
            if str(upd_params['cores']) != result['config']['resources']['cores']:
                need_update = True
            if str(upd_params['core-fraction']) != result['config']['resources']['core_fraction']:
                need_update = True
            cnf_mem = upd_params['memory']
            if cnf_mem.find('GB') != -1:
                cnf_mem = int(cnf_mem.replace('GB',''))*1024*1024*1024
            if str(cnf_mem) != result['config']['resources']['memory']:
                need_update = True
            if need_update:
                result['yc_args'] = build_cmd_line(upd_params)
                if result['config']['status'] == 'RUNNING':
                    res = get_oneline_param('yc compute instance stop '+module.params['machine'])
                    if res[0] != 0:
                        module.fail_json(msg=res[2], **result)
                res = get_oneline_param('yc compute instance update '+module.params['machine']+' '+build_cmd_line(upd_params)+' --format=json')
                if res[0] != 0:
                    module.fail_json(msg=res[2], **result)
                result['config'] = json.loads(res[1])
                result['changed'] = True
    if 'config' in result:
        if (module.params['state'] == 'exists') and (result['config']['status'] == 'STOPPED'):
            if result['config']['status'] == 'STOPPED':
                res = get_oneline_param('yc compute instance start '+module.params['machine']+' --format=json')
                if res[0] != 0:
                    module.fail_json(msg=res[2], **result)
                result['config'] = json.loads(res[1])
        try:
            result['ip'] = result['config']['network_interfaces'][0]['primary_v4_address']['one_to_one_nat']['address']
        except:
            pass
 
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
