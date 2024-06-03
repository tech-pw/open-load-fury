from datetime import datetime
import boto3
import os


def upload_report_to_s3(logger, directory_name, bucket_name, user_prefix):
    s3_client = boto3.client('s3')

    now = datetime.now()
    s3_prefix = f"{user_prefix}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}{now.minute:02d}/"

    print(f"Uploading final loadtest report to s3://{bucket_name}")
    for root, _, files in os.walk(directory_name):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, directory_name)
            s3_path = os.path.join(s3_prefix, relative_path).replace("\\", "/")

            try:
                s3_client.upload_file(local_path, bucket_name, s3_path)
                logger.info(f"Successfully uploaded {local_path} to s3://{bucket_name}/{s3_path}")
            except FileNotFoundError:
                logger.exception(f"The file was not found: {local_path}")
                return
            except Exception as e:
                logger.exception(f"An error occurred: {e}")



