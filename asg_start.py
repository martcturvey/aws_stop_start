'''
Given ASG 'Name' tag, locate ASG & start attached EC2 instances
Scaling processes are resumed
'''

import sys
import argparse
import boto3
import boto.ec2
import time

aws_region = "eu-west-2"

parser = argparse.ArgumentParser()
parser.add_argument("asg_name_tag", type=str,
		    help="The Name tag of the target ASG")
args = parser.parse_args()

ec2_connect = boto.ec2.connect_to_region(aws_region)
reservations = ec2_connect.get_all_instances(filters={'instance-state-name' : 'stopped', 'tag:Name' : args.asg_name_tag})

if len(reservations) == 0:
  print(args.asg_name_tag + ": no EC2 matches in a stopped state")
  sys.exit(2)

asg = boto3.client('autoscaling')
paginator = asg.get_paginator('describe_auto_scaling_groups')
asg_list = []
ec2_list = []

page_iterator = paginator.paginate(
  PaginationConfig={'PageSize':100}
)

filtered_asgs = page_iterator.search(
  'AutoScalingGroups[] | [?contains(Tags[?Key==`{}`].Value, `{}`)]'.format('Name', args.asg_name_tag)
)

for asg_found in filtered_asgs:
  print("ASGs:")
  print(asg_found['AutoScalingGroupName'])
  asg_list.append(asg_found)

if len(asg_list) == 0:
  print('No ASG matches')
  sys.exit(1)
elif len(asg_list) > 1:
  print('Multiple ASG matches')
  sys.exit(1)

for asg_instance in asg_list[0]['Instances']:
  ec2_list.append(asg_instance['InstanceId'])

ec2 = boto3.resource('ec2')

print("EC2s:")

started_list = []

for ec2_instance in ec2_list:
  instance = ec2.Instance(ec2_instance)
  ec2_start = instance.start()
  print(f"{ec2_start['StartingInstances'][0]['InstanceId']} is {ec2_start['StartingInstances'][0]['CurrentState']['Name']}")
  started_list.append(ec2_start['StartingInstances'][0]['InstanceId'])

# Allow metadata to be populated
time.sleep(10)

all_healthy = False
sleep_loop = 0

while (not all_healthy) and (sleep_loop < 10):
  sleep_loop += 1
  instance_healthy = 0
  for status in ec2.meta.client.describe_instance_status(InstanceIds=started_list)['InstanceStatuses']:
    if (status['SystemStatus']['Status'] == 'ok') and (status['InstanceStatus']['Status'] == 'ok'):
      print(status['InstanceId'] + " is passing status checks")
      instance_healthy += 1
    else:
      print(status['InstanceId'] + " is not passing status checks")
  if (instance_healthy < len(started_list)):
    print("Waiting for all instances to pass status checks")
    time.sleep(30)
  else:
    print("All instances passing status checks, resuming ASG scaling processes")
    all_healthy = True

if (not all_healthy) and (sleep_loop == 10):
  print("Some instances failed to pass status checks within time limit")
  sys.exit(2)

asg_resume = asg.resume_processes(
  AutoScalingGroupName=asg_list[0]['AutoScalingGroupName'],
  ScalingProcesses=[
    'Launch',
    'Terminate',
    'HealthCheck',
    'ReplaceUnhealthy',
  ],
)
