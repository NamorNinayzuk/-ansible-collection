#!/usr/bin/python3

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: file_content
short_description: Module create or read file content.
version_added: "1.0.0"
description: This module create file with delivered content or read content from existed file on host.
options:
    path:
        description: path to file
        required: true
        type: str
    content:
        description: content of the file
        required: false
        type: str
        default: ''
module return operation status - one of the following:
    - created: the file was created and content were saved to file
    - modified: the file existed and its contents overwritten (content option is not empty)
    - readed: the file existed and its content read (content option is omitted)
    - resisted: the file existed and its contents are equal to transferred
    - denied: module could not access the file - error
extends_documentation_fragment:
    - test.utils.file_content
'''

EXAMPLES = r'''
- name: Create file with content
  test.utils.file_content:
    path: test_dir/test_file
    content: "simple line"
- name: Read file content
 test.utils.file_content:
    path: test_dir/test_file
'''

RETURN = r'''
path:
    description: Path to the file which module was applied.
    type: str
    returned: always
    sample: 'test_dir/test_file'
content:
    description: File contant.
    type: str
    returned: always
    sample: 'test'
status:
    description: state of file - created, modified, readed, resisted, denied
    type: str
    returned: always
    sample: 'created'
'''

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
