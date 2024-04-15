import json
import boto3
import csv
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from AmazonCloudWatch')
    }

def get_cost_and_usage_from_s3(bucket_name, file_key):
    """
    Retrieve cost and usage data from a CSV file stored in an S3 bucket.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = response['Body'].read().decode('utf-8')
    return csv_data

def process_cost_and_usage(csv_data):
    """
    Process the retrieved cost and usage data and print specific fields.
    """
    # Parse CSV data
    cost_and_usage = []
    csv_reader = csv.DictReader(csv_data.splitlines())
    
    # Set start date and end date
    start_date = datetime(2024, 3, 1)
    end_date = datetime(2024, 4, 1)
    
    total_cost = 0  # Initialize total cost accumulator
    
    # Iterate over each row in the CSV data
    for row in csv_reader:
        product_name = row.get('product/ProductName')
        
        # Check if the product name is 'AmazonCloudWatch' and within the date range
        if product_name == 'AmazonCloudWatch':
            usage_start_date = datetime.strptime(row.get('lineItem/UsageStartDate'), '%Y-%m-%dT%H:%M:%SZ')
            if start_date <= usage_start_date <= end_date:
                # Extract cost and convert it to float
                cost = float(row.get('lineItem/UnblendedCost', '0'))
                total_cost += cost  # Add cost to the total
                
                # Print details
                print("ResourceId:", row.get('lineItem/ResourceId'))
                print("Product:", product_name)
                print("UnblendedCost:", row.get('lineItem/UnblendedCost'))
                lambda_arn = row.get('lineItem/ResourceId')
                iam_role_name = extract_iam_role_from_lambda_arn(lambda_arn)
                print("IAM Role Name:", iam_role_name)
                print()  # Print a blank line for readability
                
    # Print the total cost
    print("Total Cost for Amazon CloudWatch from March 01, 2024, to April 01, 2024:", total_cost)


def extract_iam_role_from_lambda_arn(lambda_arn):
    """
    Extract IAM role name from Lambda ARN.
    """
    # CloudWatch ARN format: arn:aws:cloudwatch:<region>:<account_id>:<resource_type>/<resource_id>
    parts = lambda_arn.split(':')
    if len(parts) >= 7:
        iam_role_name = parts[-1]  # Last component is IAM role name
        if iam_role_name.startswith('/aws/lambda/'):
            return iam_role_name[len('/aws/lambda/'):]  # Remove the '/aws/lambda/' prefix
        else:
            return iam_role_name
    else:
        return None

bucket_name = 'reportbuket'
file_key = 'Team3report-00001Test.csv'

# Retrieve cost and usage data from S3
csv_data = get_cost_and_usage_from_s3(bucket_name, file_key)

# Process and print specific fields from the retrieved data
process_cost_and_usage(csv_data)
