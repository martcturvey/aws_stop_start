# ec2_start.py
#
# Given EC2 'Name' tag, start EC2 instances

import sys
import argparse
import boto3
import boto.ec2

parser = argparse.ArgumentParser()
parser.add_argument("ec2_name_tag", type=str,
		    help="The Name tag of the target EC2 instance(s)")
args = parser.parse_args()

ec2_connect = boto2.ec2.connect_to_region('eu-west-2')
reservations = ec2_connect.get_all_instances(filters={'instance-state-name' : 'stopped', 'tag:Name':args.ec2_name_tag+'*'})

if len(reservations) == 0:
  print('No EC2 matches')
  sys.exit(1)

ec2 = boto3.resource('ec2')

print("EC2s:")

for res in reservations:
  for inst in res.instances:
    target_instance = ec2.Instance(inst.id)
    ec2_start = target_instance.start()
    print(ec2_start['StartingInstances'][0]['InstanceId'] + ' is ' + ec2_start['StartingInstances'][0]['CurrentState']['Name'])
