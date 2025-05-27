import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError


class S3Uploader:
    AWS_BUCKET_NAME = "emr-project3"
    AWS_REGION = "us-east-1"
    AWS_ACCESS_KEY = ""
    AWS_SECRET_KEY = ""
    AWS_SESSION_TOKEN = ""

    @staticmethod
    def upload_file_to_public_s3(
        file_path,
        bucket_name,
        object_name=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
    ):
        """Upload a file to a public S3 bucket with optional explicit credentials.

        If credentials are not provided, this function relies on the S3 bucket policy
        allowing public write access and potentially on AWS region configuration being
        available in the environment or default configuration files.

        :param file_path: Path to the file to upload.
        :param bucket_name: Name of the public S3 bucket.
        :param object_name: S3 object name. If not specified, file_path is used.
        :param aws_access_key_id: AWS access key ID.
        :param aws_secret_access_key: AWS secret access key.
        :param aws_session_token: AWS session token (academy accounts).
        :return: True if file was uploaded, else False.
        """
        # If S3 object_name was not specified, use the base name of the file
        if object_name is None:
            object_name = os.path.basename(file_path)

        # Create an S3 client. Pass credentials if provided.
        try:
            if aws_access_key_id and aws_secret_access_key:
                s3_client = boto3.client(
                    "s3",
                    region_name="us-east-1",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token,
                )
            else:
                s3_client = boto3.client("s3", region_name="us-east-1")

        except Exception as e:
            print(f"Error creating S3 client: {e}")
            print(
                "Ensure AWS region is configured in environment variables (e.g., AWS_REGION) or config files."
            )
            return False

        try:
            s3_client.upload_file(file_path, bucket_name, "raw/" + object_name)
            print(
                f"File '{file_path}' successfully uploaded to '{bucket_name}/raw/{object_name}'"
            )
            os.remove(file_path)
            print(f"Local file '{file_path}' deleted.")
            return True
        except FileNotFoundError:
            print(f"Error: The file was not found at '{file_path}'")
            return False
        except NoCredentialsError:
            print("Error: AWS credentials not found.")
            print(
                "Although the bucket is public, boto3 might still require region configuration."
            )
            print(
                "Ensure AWS region is configured in environment variables (e.g., AWS_REGION) or config files."
            )
            return False
        except PartialCredentialsError:
            print("Error: Incomplete AWS credentials found.")
            print(
                "Although the bucket is public, boto3 might still require region configuration."
            )
            print(
                "Ensure AWS region is configured in environment variables (e.g., AWS_REGION) or config files."
            )
            return False
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            if e.response["Error"]["Code"] == "AccessDenied":
                print(
                    "Permission denied. The S3 bucket might not be configured for public write access."
                )
            return False
        except Exception as e:
            print(f"An unexpected error occurred during upload: {e}")
            return False
