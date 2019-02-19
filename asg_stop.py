# asg_stop.py
# 
# Given ASG 'Name' tag, locate ASG & stop attached EC2 instances
# Scaling processes are suspended

import sys
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("asg_name_tag", type=str,
		    help="The Name tag of the target ASG")
args = parser.parse_args()

asg = boto3.client('autoscaling')
paginator = asg.get_paginator('describe_auto_scaling_groups')
asg_list = []
ec2_list = []

page_iterator = paginator.paginate(
  PaginationConfig={'PageSize':100}
}

filtered_asgs = page_iterator.search(
  'AutoScalingGroups[] | [?contains(Tags[?Key==`{}`].Value, `{}`)]'.format('Name', args.asg_name_tag)
)

for asg_found in filtered_asgs:
  print("ASGs:")
  print(asg_found['AutoScalingGroupName'])
  asg_list.append(asg_found)
)

asg_count = len(asg_list)

if asg_count == 0:
  print('No ASG matches')
  sys.exit(1)
elif asg_count > 1:
  print('Multiple ASG matches')
  sys.exit(1)

for asg_instance in asg_list[0]['Instances']:
  ec2_list.append(asg_instance['InstanceId'])

asg_suspend = asg.suspend_processes(
  AutoScalingGroupName=asg_list[0]['AutoScalingGroupName'],
  ScalingProcesses=[
    'Launch',
    'Terminate',
    'HealthCheck',
    'ReplaceUnhealthy',
  ],
)

ec2 = boto.resource('ec2')

print("EC2s:")

for ec2_instance in ec2_list:
  instance = ec2.Instance(ec2_instance)
  ec2_stop = instance.stop()
  print(ec2_stop['StoppingInstances'][0]['InstanceId'] + ' is ' + ec2_stop['StoppingInstances'][0]['CurrentState']['Name'])

