import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import json
import uuid
from typing import Optional, Dict, Any
from app.core.config import settings


class AWSService:
    def __init__(self):
        # Configure boto3 with retry logic
        config = Config(
            region_name=settings.AWS_REGION,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config,
        )

        self.sqs_client = boto3.client(
            "sqs",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config,
        )

    def generate_presigned_url(
        self,
        file_name: str,
        content_type: str,
        expiration: int = settings.S3_PRESIGNED_URL_EXPIRATION,
    ) -> tuple[str, str]:
        # Generate unique S3 key
        file_extension = file_name.split(".")[-1] if "." in file_name else "mp3"
        s3_key = f"audio-uploads/{uuid.uuid4()}.{file_extension}"

        try:
            presigned_url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.S3_BUCKET_NAME,
                    "Key": s3_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expiration,
            )
            return presigned_url, s3_key
        except ClientError as e:
            raise Exception(f"Error generating presigned URL: {str(e)}")

    def delete_audio_file(self, s3_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting S3 object {s3_key}: {str(e)}")
            return False

    def check_file_exists(self, s3_key: str) -> bool:

        try:
            self.s3_client.head_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
            return True
        except ClientError:
            return False

    def send_processing_job(
        self,
        session_id: str,
        therapist_id: str,
        patient_id: str,
        s3_key: str,
        audio_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        message_body = {
            "session_id": str(session_id),
            "therapist_id": str(therapist_id),
            "patient_id": str(patient_id),
            "s3_key": s3_key,
            "audio_metadata": audio_metadata or {},
        }

        try:
            response = self.sqs_client.send_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    "SessionId": {"StringValue": str(session_id), "DataType": "String"},
                    "TherapistId": {
                        "StringValue": str(therapist_id),
                        "DataType": "String",
                    },
                },
            )
            return response.get("MessageId")
        except ClientError as e:
            print(f"Error sending SQS message: {str(e)}")
            return None

    def get_file_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.s3_client.head_object(
                Bucket=settings.S3_BUCKET_NAME, Key=s3_key
            )
            return {
                "size": response.get("ContentLength"),
                "content_type": response.get("ContentType"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag"),
            }
        except ClientError as e:
            print(f"Error getting file metadata for {s3_key}: {str(e)}")
            return None


# Singleton instance
aws_service = AWSService()
