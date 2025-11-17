import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Client:

    def __init__(self):
        self.client = boto3.client("s3")
        logger.info("S3 client initialized")

    def download_file_stream(self, bucket: str, key: str) -> bytes:
        try:
            logger.info(f"Downloading s3://{bucket}/{key}")

            response = self.client.get_object(Bucket=bucket, Key=key)
            file_content = response["Body"].read()

            file_size_mb = len(file_content) / (1024 * 1024)
            logger.info(f"Downloaded {file_size_mb:.2f}MB from S3")

            return file_content

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"S3 download failed: {error_code} - {str(e)}")
            raise

    def delete_file(self, bucket: str, key: str) -> bool:
        try:
            logger.info(f"Deleting s3://{bucket}/{key}")

            self.client.delete_object(Bucket=bucket, Key=key)

            logger.info(f"Successfully deleted s3://{bucket}/{key}")
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"S3 deletion failed: {error_code} - {str(e)}")
            return False

    def get_object_metadata(self, bucket: str, key: str) -> dict:
        try:
            response = self.client.head_object(Bucket=bucket, Key=key)

            metadata = {
                "content_length": response.get("ContentLength", 0),
                "content_type": response.get("ContentType", "unknown"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag", "").strip('"'),
            }

            logger.info(f"Retrieved metadata for s3://{bucket}/{key}")
            return metadata

        except ClientError as e:
            logger.error(f"Failed to get metadata: {str(e)}")
            raise


class SQSClient:
    def __init__(self):
        self.client = boto3.client("sqs")
        logger.info("SQS client initialized")

    def send_message(
        self, queue_url: str, message_body: dict, delay_seconds: int = 0
    ) -> str:
        try:
            import json

            response = self.client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body),
                DelaySeconds=delay_seconds,
            )

            message_id = response.get("MessageId")
            logger.info(f"Sent message to SQS: {message_id}")

            return message_id

        except ClientError as e:
            logger.error(f"Failed to send SQS message: {str(e)}")
            raise

    def change_message_visibility(
        self, queue_url: str, receipt_handle: str, visibility_timeout: int
    ) -> bool:
        try:
            self.client.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=visibility_timeout,
            )

            logger.info(f"Changed message visibility to {visibility_timeout}s")
            return True

        except ClientError as e:
            logger.error(f"Failed to change message visibility: {str(e)}")
            return False
