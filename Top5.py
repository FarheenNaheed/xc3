import json
import boto3
import csv
from io import StringIO

def lambda_handler(event, context):
    """
    Lambda function handler. Invoked when the Lambda function is triggered.

    Parameters:
    event: Event data passed to the function during invocation.
    context: Runtime information about the function execution environment.

    Returns:
    A dictionary with status code 200 and a greeting message.
    """
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Resources')
    }

def get_cost_and_usage_from_s3(bucket_name, file_key):
    """
    Retrieve cost and usage data from a CSV file stored in an S3 bucket.
    Parameters:
    bucket_name: Name of the S3 bucket containing the CSV file.
    file_key: Key (path) of the CSV file in the S3 bucket.

    Returns:
    A list of dictionaries representing rows from the CSV file.
    """
    # Create an S3 client to interact with the S3 service
    s3 = boto3.client('s3')
     # Get the CSV file from the specified bucket and file key
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
     # Read and decode the contents of the CSV file
    csv_data = response['Body'].read().decode('utf-8')
    
    # Parse CSV data
    cost_and_usage = []
    csv_reader = csv.DictReader(StringIO(csv_data))
    for row in csv_reader:
        cost_and_usage.append(row)
    
    return cost_and_usage
def extract_resource_details_from_arn(resource_arn):
    """
    Extracts resource details from a resource ARN based on the service type.
    Handles different ARN formats for various AWS services.
    
    Parameters:
    resource_arn: The ARN (Amazon Resource Name) from which to extract the resource details.
    
    Returns:
    A dictionary containing relevant resource details, such as IAM role name, function name, bucket name, topic name, etc.,
    based on the service type, or None if unable to extract.
    """
    # Check if the ARN is provided
    if not resource_arn:
        return None
    
    # Split the ARN into parts
    parts = resource_arn.split(':')
    
    # Ensure there are enough parts in the ARN
    if len(parts) < 6:
        return None
    
    # Determine the service type
    service_type = parts[2]  # This is the third element in the ARN
    
    # Create a dictionary to hold the extracted details
    resource_details = {}
    
    # Handle different service types
    if service_type == 'lambda':
        # For Lambda ARN, extract the function name
        function_name = parts[-1].split(':')[1] if ':' in parts[-1] else parts[-1].split('/')[-1]
        resource_details['function_name'] = function_name
    elif service_type == 's3':
        # For S3 ARN, extract the bucket name and optionally the object key
        if 'bucket' in resource_arn:
            resource_details['bucket_name'] = parts[-1]
        else:
            # For object ARN, extract both bucket and object key
            s3_parts = parts[5].split('/', 1)
            resource_details['bucket_name'] = s3_parts[0]
            resource_details['object_key'] = s3_parts[1] if len(s3_parts) > 1 else None
    elif service_type == 'sns':
        # For SNS ARN, extract the topic name
        topic_name = parts[-1]
        resource_details['topic_name'] = topic_name
    elif service_type == 'sqs':
        # For SQS ARN, extract the queue name
        queue_name = parts[-1]
        resource_details['queue_name'] = queue_name
    elif service_type == 'ec2':
        # For EC2 ARN, extract the instance ID or other resources
        # e.g., network-interface, elastic-ip, or natgateway
        resource_type = parts[5].split('/')[0]
        resource_id = parts[5].split('/')[-1]
        resource_details['resource_type'] = resource_type
        resource_details['resource_id'] = resource_id
    elif service_type == 'wafv2':
        # For WAF ARN, extract the web ACL name or rule group
        resource_type = parts[5].split('/')[0]
        resource_id = parts[5].split('/')[-1]
        resource_details['resource_type'] = resource_type
        resource_details['resource_id'] = resource_id
    elif service_type == 'dynamodb':
        # For DynamoDB ARN, extract the table name
        table_name = parts[-1].split('/')[1]
        resource_details['table_name'] = table_name
    # Add more conditions for other services as needed
    
    # Return the extracted details as a dictionary
    return resource_details
def process_cost_and_usage(cost_and_usage):
    """
    Process the retrieved cost and usage data and print the top 5 most expensive resources for each service.
    Additionally, calculate and print the cumulative cost per service.

    Parameters:
    cost_and_usage: A list of dictionaries representing rows from the CSV file.

    Returns:
    None. Prints the top 5 most expensive resources for each service and the cumulative cost per service.
    """
    # Dictionary to store resource costs for each service
    service_costs = {}
    # Dictionary to store cumulative cost per service
    cumulative_costs_per_service = {}

    # Process each entry in the cost and usage data
    for entry in cost_and_usage:
        product_name = entry.get('product/servicecode')
        if product_name:
            # Extract usage amount and unblended cost
            usage_amount = float(entry.get('lineItem/UsageAmount'))
            unblended_cost = float(entry.get('lineItem/UnblendedCost'))
            resource_arn = entry.get('lineItem/ResourceId')  # Extract resource ARN (Amazon Resource Name)

            # Extract resource details using the ARN
            resource_details = extract_resource_details_from_arn(resource_arn)

            # Store usage and cost data for each service
            if product_name in service_costs:
                service_costs[product_name].append((usage_amount, unblended_cost, resource_arn, resource_details))
            else:
                service_costs[product_name] = [(usage_amount, unblended_cost, resource_arn, resource_details)]

            # Calculate cumulative cost per service
            if product_name in cumulative_costs_per_service:
                cumulative_costs_per_service[product_name] += unblended_cost
            else:
                cumulative_costs_per_service[product_name] = unblended_cost

    # Sort the resources for each service by cost in descending order and keep the top 5
    for service, costs in service_costs.items():
        sorted_costs = sorted(costs, key=lambda x: x[1], reverse=True)
        service_costs[service] = sorted_costs[:5]  # Store only top 5 expensive resources

    # Print the top 5 expensive resources for each service
    for service, costs in service_costs.items():
        print(f"Top 5 Expensive Resources for {service}:")
        for i, (usage_amount, unblended_cost, resource_arn, resource_details) in enumerate(costs, 1):
            print(f"{i}. ARN: {resource_arn}, Usage Amount: {usage_amount}, Unblended Cost: {unblended_cost}")
            # Print IAM role name if available
            if resource_details and 'function_name' in resource_details:
                print(f"IAM Role Name: {resource_details['function_name']}")

        # Print the cumulative cost per service
        cumulative_cost = cumulative_costs_per_service[service]
        print(f"Cumulative Cost for {service}: {cumulative_cost:.2f}")
# Using the existing S3 bucket details for CUR reports
bucket_name = 'reportbuket'
file_key = 'Team3report-00001_New.csv'
# Retrieve cost and usage data from S3
cost_and_usage = get_cost_and_usage_from_s3(bucket_name, file_key)

# Process and print top 5 expensive resources for each service
process_cost_and_usage(cost_and_usage)
