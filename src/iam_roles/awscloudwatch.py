import json
import boto3
import csv
from io import StringIO
from collections import defaultdict

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from CloudWatch')
    }

def get_cost_and_usage_from_s3(bucket_name, file_key):
    """
    Retrieves cost and usage data from Cost and Usage report CSV file stored in an S3 bucket.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = response['Body'].read().decode('utf-8')
    
    # Parse CSV data
    cost_and_usage = []
    csv_reader = csv.DictReader(StringIO(csv_data))
    for row in csv_reader:
        cost_and_usage.append(row)
    
    return cost_and_usage

def calculate_cumulative_costs(cost_and_usage):
    """
    Calculate the cumulative costs of Amazon CloudWatch for each resource.
    """
    cumulative_costs = defaultdict(float)
    for entry in cost_and_usage:
        product_name = entry.get('product/servicecode')
        if product_name == 'AmazonCloudWatch':
            resource_id = entry.get('lineItem/ResourceId')
            # Extract substring after the last '/'
            resource_name = resource_id.split('/')[-1]
            usage_amount = float(entry.get('lineItem/UsageAmount', 0))
            unblended_cost = float(entry.get('lineItem/UnblendedCost', 0))
            # Sum up the costs for each resource
            cumulative_costs[resource_name] += unblended_cost
    
    return cumulative_costs

# Using the existing S3 bucket details for CUR reports
bucket_name = 'reportbuket'
file_key = 'Team3report-00001_New.csv'

# Retrieve cost and usage data from S3
cost_and_usage = get_cost_and_usage_from_s3(bucket_name, file_key)

# Calculate cumulative costs for each resource
cumulative_costs = calculate_cumulative_costs(cost_and_usage)

# Print cumulative monthly costs for each resource
for resource_name, cost in cumulative_costs.items():
    print(f"Resource Name: {resource_name}, Cumulative Cost: ${cost:.6f}")
