#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_os_default_template
short_description: Manage Foreman Operatingsystem default templates using Foreman API v2
description:
- Create,update and delete Foreman Operatingsystem default templates using Foreman API v2
options:
  operatingsystem:
    description: Operatingsystem name
    required: true
    default: None
  config_template:
    description: Config Template name
    required: true
    default: None
  template_kind:
    description: Template kind
    required: true
    default: None
  state:
    description: OS Default template state
    required: false
    default: 'present'
    choices: ['present', 'absent']
  foreman_host:
    description: Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description: Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description: Username to be used to authenticate on Foreman
    required: true
    default: null
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure OS Default Template
  foreman_os_default_template:
    operatingsystem: CoreOS
    config_template: CoreOS PXELinux
    template_kind: PXELinux
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
    os_name = module.params['operatingsystem']
    config_template_name = module.params['config_template']
    template_kind_name = module.params['template_kind']
    state = module.params['state']

    try:
        os = theforeman.search_operatingsystem(data=dict(name=os_name))
    except ForemanError as e:
        module.fail_json(msg='Could not search operatingsystem: {0}'.format(e.message))

    if not os:
        module.fail_json(msg='Operatingsystem {os_name} not found'.format(os_name=os_name))

    try:
        config_templates = theforeman.get_config_templates()
    except:
        module.fail_json(msg='Could not get config templates: {0}'.format(e.message))

    config_template = None
    for item in config_templates:
        if item.get('name') == config_template_name and item.get('template_kind_name') == template_kind_name:
            config_template = item
            break

    if not config_template:
        module.fail_json(msg='Could not find config template {config_template} of kind {template_kind}'.format(
            config_template_name=config_template_name, template_kind=template_kind_name))

    try:
        os_default_templates = theforeman.get_operatingsystem_default_templates(id=os.get('id'))
    except ForemanError as e:
        module.fail_json(msg='Could not get operatingsystem default templates: {0}'.format(e.message))

    os_default_template = None
    for item in os_default_templates:
        if (item.get('config_template_id') == config_template.get('id')) and (
                    item.get('template_kind_id') == config_template.get('template_kind_id')):
            os_default_template = item
            break

    if state == 'absent':
        if os_default_template:
            try:
                os_default_template = theforeman.delete_operatingsystem_default_template(id=os.get('id'),
                                                                                         template_id=os_default_template.get(
                                                                                             'id'))
            except:
                module.fail_json(msg='Could not delete operatingsystem default template: {0}'.format(e.message))
            return True, os_default_template
        return False, os_default_template

    if not os_default_template:
        try:
            os_default_template = theforeman.create_operatingsystem_default_template(id=os.get('id'), data=dict(
                config_template_id=config_template.get('id'), template_kind_id=config_template.get('template_kind_id')))
        except ForemanError as e:
            module.fail_json(msg='Could not create operatingsystem default template: {0}'.format(e.message))
        return True, os_default_template

    return False, os_default_template


def main():
    global module
    global theforeman

    module = AnsibleModule(
        argument_spec=dict(
            operatingsystem=dict(type='str', required=True),
            config_template=dict(type='str', required=True),
            template_kind=dict(type='str', required=True),
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

    changed, os_default_template = ensure()
    module.exit_json(changed=changed, os_default_template=os_default_template)

# import module snippets
from ansible.module_utils.basic import *

main()

