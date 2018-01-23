#!/usr/bin/env python

from ansible.module_utils.basic import *
from heroku3 import from_key


def env_present(params, app):
    current_value = app.config().to_dict().get(params['key'])
    if current_value != params['value']:
        app.config()[params['key']] = params['value']
        return True, {}
    return False, {}


def env_absent(params, app):
    if params['key'] in app.config():
        del app.config()[params['key']]
        return True, {}
    return False, {}


def main():
    fields = {
        "api_key": {"required": True, "type": "str"},
        "app": {"required": True, "type": "str"},
        "key": {"required": True, "type": "str"},
        "value": {"required": False, "default": "", "type": "str"},
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": 'str'
        },
    }
    choice_map = {
        'present': env_present,
        'absent': env_absent,
    }

    module = AnsibleModule(argument_spec=fields)

    conn = from_key(module.params['api_key'])
    app = conn.apps()[module.params['app']]
    has_changed, result = choice_map.get(module.params['state'])(module.params, app)
    module.exit_json(changed=has_changed, meta=result)


if __name__ == '__main__':
    main()
