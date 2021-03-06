#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_ptable
short_description: Manage Foreman Partition Tables using Foreman API v2
description:
- Create, update and delete Foreman Partition Tables using Foreman API v2
options:
  name:
    description:
    - Partition Table name
    required: true
    default: null
    aliases: []
  layout:
    description:
    - Partition Table layout
    required: false
  state:
    description:
    - Partition Table state
    required: false
    default: 'present'
    choices: ['present', 'absent']
  foreman_host:
    description:
    - Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description:
    - Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description:
    - Username to be used to authenticate on Foreman
    required: true
    default: null
  foreman_pass:
    description:
    - Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure Partition Table
  foreman_ptable:
    name: FreeBSD
    layout: 'some layout'
    state: present
    foreman_user: admin
    foreman_pass: secret
    foreman_host: foreman.example.com
    foreman_port: 443
'''

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True


def ensure():
    name = module.params['name']
    layout = module.params['layout']
    state = module.params['state']

    data = dict(name=name)

    try:
        ptable = theforeman.search_partition_table(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get partition table: {0}'.format(e.message))

    data['layout'] = layout

    if not ptable and state == 'present':
        try:
            ptable = theforeman.create_partition_table(data)
        except ForemanError as e:
            module.fail_json(msg='Could not create partition table: {0}'.format(e.message))
        return True, ptable

    if ptable and state == 'absent':
        try:
            ptable = theforeman.delete_architecture(id=ptable.get('id'))
        except ForemanError as e:
            module.fail_json(msg='Could not delete partition table: {0}'.format(e.message))
        return True, ptable

    return False, ptable


def main():
    global module
    global theforeman

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            layout=dict(type='str', required=False),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    changed, ptable = ensure()
    module.exit_json(changed=changed, ptable=ptable)

# import module snippets
from ansible.module_utils.basic import *

main()
