'''
Given RDS DB identifier, starts instance
'''

import sys
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("rds_name", type=str,
		    help="The Name tag of the target RDS")
args = parser.parse_args()

rds = boto3.client('rds')

rds_found = rds.describe_db_instances(
  DBInstanceIdentifier = args.rds_name
)

if len(rds_found['DBInstances']) == 0:
  print('No RDS matches')
  sys.exit(1)
elif len(rds_found['DBInstances']) > 1:
  print('Multiple RDS matches')
  sys.exit(1)

if rds_found['DBInstances'][0]['DBInstanceStatus'] != 'stopped':
  print('RDS state is not stopped')
  sys.exit(1)

print(f"RDS {args.rds_name} is {rds_found['DBInstances'][0]['DBInstanceStatus']}. Starting now")

rds_start = rds.start_db_instance(
  DBInstanceIdentifier = args.rds_name
)
