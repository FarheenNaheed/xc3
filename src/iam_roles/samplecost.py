import boto3
from datetime import datetime, timedelta

def get_cost_breakdown_for_role(role_name):
    client = boto3.client('ce')

    # Define the time range for the cost data (e.g., last 7 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    # Get the costs by service and group by the IAM role tag
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'TAG',
                'Key': 'iam_role'
            },
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    # Print the cost breakdown for the IAM role
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            value = group['Metrics']['BlendedCost']['Amount']
            #print(f"IAM Role: {group['Keys'][0]}, Service: {group['Keys'][1]}, Cost: {value}")
            print(f"Service: {group['Keys'][1]}, Cost: {value}")
if __name__ == "__main__":
    # Specify the IAM roles for which you want to retrieve cost breakdown
    #iam_roles = ['monikaxc3-total_account_cost-role', 'monikaxc3-most_expensive_service_role']
    #iam_roles = ['monikaxc3-total_account_cost-role']
    iam_roles = ['AdminRole']
    for role in iam_roles:
        get_cost_breakdown_for_role(role)
