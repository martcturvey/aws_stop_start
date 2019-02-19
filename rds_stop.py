# rds_stop.py
#
# Given RDS DB identifier, stops instance

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

rds_count = len(rds_found['DBInstances'])

if rds_count == 0:
  print('No RDS matches')
  sys.exit(1)
elif rds_count > 1:
  print('Multiple RDS matches')
  sys.exit(1)

if rds_found['DBInstances'][0]['DBInstanceStatus'] != 'available':
  print('RDS state is not available')
  sys.exit(1)

print('RDS ' + args.rds_name + ' is ' + rds_found['DBInstances'][0]['DBInstanceStatus'] + '. Stopping now')

rds_stop = rds.stop_db_instance(
  DBInstanceIdentifier = args.rds_name
)
