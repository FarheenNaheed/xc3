import os
import re
import io
import gzip
import logging
import boto3
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from urllib.parse import unquote_plus

try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    lambda_client = boto3.client("lambda")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    """
    Lambda handler function that extracts IAM role information and pushes it to Prometheus.

    Parameters:
    - event (dict): The event payload containing the list of roles.
    - context (object): The context object that provides information about the runtime environment.

    Returns:
    - dict: The response with a status code of 200 and a message body of "IAM Roles".
    """

    list_of_iam_roles = []
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    if "resources" in key:
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            resource_file = response["Body"].read()
            with gzip.GzipFile(fileobj=io.BytesIO(resource_file), mode="rb") as data:
                list_of_iam_roles = json.load(data)
        except Exception as e:
            logging.error(
                "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                    key, bucket
                )
            )
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    logging.info(list_of_iam_roles)

    account_id = context.invoked_function_arn.split(":")[4]

    registry = CollectorRegistry()
    iam_role_all_gauge = Gauge(
        "IAM_Role_All",
        "XCCC All IAM Roles",
        labelnames=["iam_role_all", "iam_role_all_region", "iam_role_all_account"],
        registry=registry,
    )

    functionName = os.environ["func_name_iam_role_service_mapping"]
    iam_role_service_lambda_payload = lambda_client.invoke(
        FunctionName=functionName,
        InvocationType="Event",
        Payload=json.dumps(list_of_iam_roles),
    )

    for role in list_of_iam_roles:
        role_name = role["RoleName"]
        region = role["RoleLastUsed"].get("Region", "None")
        iam_role_all_gauge.labels(role_name, region, account_id).set(0)

    push_to_gateway(os.environ["prometheus_ip"], job="IAM-roles-all", registry=registry)
    return {"statusCode": 200, "body": "IAM Roles"}