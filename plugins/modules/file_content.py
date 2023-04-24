#!/usr/bin/python3

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os

def run_module():

    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=False, default='')
    )
    result = dict(
        changed=False,
        path='',
        content='',
        status='denied'
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result['path'] = module.params['path']
    result['content'] = module.params['content']

    go_write = False
    result['path'] = module.params['path']
    if os.path.isfile(result['path']):
        try:
            with open(result['path'],'r') as f:
                data = f.read()
        except:
            module.fail_json(msg='Can`t open file. Check file path and access rights.', **result)
        if result['content'] == '':
            result['content'] = data
            result['status'] = 'readed'
        elif data == result['content']:
            result['status'] = 'resisted'
        else:
            result['status'] = 'modified'
            go_write = True
    elif not os.path.exists(result['path']):
        result['status'] = 'created'
        go_write = True
    else:
        module.fail_json(msg='Path is directory.', **result)

    if go_write:
        result['changed'] = True
        if not module.check_mode:
            try:
                with open(result['path'],'w') as f:
                    f.write(result['content'])
            except:
                result['status'] = 'denied'
                module.fail_json(msg='Can`t write to file. Check file path and access rights.', **result)
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
