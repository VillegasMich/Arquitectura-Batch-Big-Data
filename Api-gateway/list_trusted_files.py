import json
import boto3

AWS_BUCKET_NAME = "emr-project3"
AWS_TUSTED_PREFIX = "trusted/"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_SESSION_TOKEN = ""

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
)


def lambda_handler(event, context):
    response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=AWS_TUSTED_PREFIX)

    if "Contents" not in response:
        return {"statusCode": 200, "body": json.dumps([])}

    files = [obj["Key"] for obj in response["Contents"]]

    return {"statusCode": 200, "body": json.dumps(files)}
