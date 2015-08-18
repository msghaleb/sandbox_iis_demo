#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_instance_facts
version_added: "1.5"
short_description: Return a list of ec2 instances, possibly filtered by tag
description:
     - Return a list of ec2 instances, possibly filtered by tag. This module has a dependency on python-boto >= 2.5
options:
  name:
    description:
      - Filter returned instances by this name.
    required: false
    default: null
    aliases: []
  instance_ids:
    description:
      - Filter returned instances by membership in a list of ids.
    required: false
    default: null
    aliases: []
  states:
    description:
      - Filter returned instances by instance state.
    required: false
    default: null
    aliases: []
  tags:
    description:
      - Filter returned instances by existence of the given tags.
    required: false
    default: null
    aliases: []
  ec2_url:
    description:
      - Url to use to connect to EC2 or your Eucalyptus cloud (by default the module will use EC2 endpoints).  Must be specified if region is not used. If not set then the value of the EC2_URL environment variable, if any, is used
    required: false
    default: null
    aliases: []
  aws_secret_key:
    description:
      - AWS secret key. If not set then the value of the AWS_SECRET_KEY environment variable is used. 
    required: false
    default: null
    aliases: [ 'ec2_secret_key', 'secret_key' ]
  aws_access_key:
    description:
      - AWS access key. If not set then the value of the AWS_ACCESS_KEY environment variable is used.
    required: false
    default: null
    aliases: ['ec2_access_key', 'access_key' ]
  region:
    description:
      - The AWS region to use.  Must be specified if ec2_url is not used. If not specified then the value of the EC2_REGION environment variable, if any, is used.
    required: false
    default: null
    aliases: [ 'aws_region', 'ec2_region' ]
requirements: [ "boto" ]
author: Scott Anderson
'''

EXAMPLES = '''
- name: Obtain list of existing instances filtered by environment tag, sorted by the parrot-count tag.
  local_action:
    module: ec2_instance_facts
    tags:
      environment: "{{ my_environment_tag_value }}"
    sorts:
      - "name"
      - "-tag:parrot-count"
    region: us-west-1
    aws_access_key: xxxxxxxxxxxxxxxxxxxxxxx
    aws_secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  register: ami_facts
Returns a list of instance dictionaries with the following information:
{
    'id': ID of the ec2 instance, such as i-1234abcd
    'image_id': ID of the AMI used to create the instance
    'ami_launch_index': The index of this particular instance amongst all those launched from the AMI
    'private_ip': The private subnet numeric IP address
    'private_dns_name': The private subnet DNS name
    'public_ip': The public IP address, if any
    'dns_name': The public DNS name, if any
    'public_dns_name': The public DNS name, if any
    'architecture': The machine architecture of the instance
    'key_name': The name of the key pair associated with this instance at launch
    'placement': The instance placement group
    'hypervisor': The hypervisor type of the instance
    'kernel': The kernel used by the instance
    'ramdisk': The ramdisk used by the instance
    'launch_time': The time at which the instance was launched
    'instance_type': The ec2 instance type; e.g. m1.medium
    'root_device_type': The root device type used by the AMI
    'root_device_name': The name of the root device
    'state': The current instance state; e.g. running, stopped, terminated, etc.
    'state_code': The numeric status code of the instance's state
}
'''
import sys
import time

from operator import itemgetter

try:
    import boto
    import boto.ec2
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)

def get_instance_info(inst):
    """
    Retrieves instance information from an instance
    ID and returns it as a dictionary
    """
    instance_info = {'id': inst.id,
                     'ami_launch_index': inst.ami_launch_index,
                     'private_ip': inst.private_ip_address,
                     'private_dns_name': inst.private_dns_name,
                     'public_ip': inst.ip_address,
                     'dns_name': inst.dns_name,
                     'public_dns_name': inst.public_dns_name,
                     'state_code': inst.state_code,
                     'architecture': inst.architecture,
                     'image_id': inst.image_id,
                     'key_name': inst.key_name,
                     'placement': inst.placement,
                     'kernel': inst.kernel,
                     'ramdisk': inst.ramdisk,
                     'launch_time': inst.launch_time,
                     'instance_type': inst.instance_type,
                     'root_device_type': inst.root_device_type,
                     'root_device_name': inst.root_device_name,
                     'state': inst.state,
                     'hypervisor': inst.hypervisor}
    try:
        instance_info['virtualization_type'] = getattr(inst,'virtualization_type')
    except AttributeError:
        instance_info['virtualization_type'] = None

    return instance_info

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            name = dict(),
            instance_ids = dict(),
            states = dict(),
            tags = dict(type='dict'),
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)

    instance_ids = module.params.get('instance_ids')
    tags = module.params.get('tags')
    states = module.params.get('states')
    name = module.params.get('name')

    ec2 = ec2_connect(module)

    try:
        filters = {}
        if name:
            filters['tag:Name'] = name
        if states:
            filters['instance-state-name'] = states
        if tags:
            for key in tags.keys():
                filters['tag:' + key] = tags[key]
        reservations = ec2.get_all_instances(instance_ids=instance_ids, filters=filters)
    except boto.exception.BotoServerError, e:
        module.fail_json(msg = "%s: %s" % (e.error_code, e.error_message))

    instances = []
    instances_by_name = {}
    for res in reservations:
        for instance in res.instances:
            instance_info = get_instance_info(instance)
            instances.append(instance_info)
            instances_by_name[instance.tags.get('Name', instance.id)] = instance_info

    module.exit_json(changed=False,
                     instances=instances,
                     instances_by_name=instances_by_name,
                     )


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

main()