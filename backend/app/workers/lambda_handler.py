import json
import logging
import os
import traceback
from typing import Dict, Any

from app.core.config import settings
from app.services.processing import SessionProcessor
from app.services.processing.database import Database

logger = logging.getLogger()
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Lambda invoked with {len(event.get('Records', []))} SQS messages")

    results = {"successful": [], "failed": []}
    db = Database(settings.DATABASE_URL)

    try:
        for record in event.get("Records", []):
            try:
                message_body = json.loads(record["body"])
                logger.info(f"Processing message: {message_body}")

                session_id = message_body.get("session_id")
                s3_key = message_body.get("s3_key")

                if not all([session_id, s3_key]):
                    raise ValueError(
                        f"Missing required fields (session_id, s3_key) in message: {message_body}"
                    )

                processor = SessionProcessor(db)
                result = processor.process_session(
                    session_id=session_id,
                    s3_bucket=settings.S3_BUCKET_NAME,
                    s3_key=s3_key,
                )

                results["successful"].append(
                    {"session_id": session_id, "result": result}
                )

                logger.info(f"Successfully processed session {session_id}")

            except Exception as e:
                error_msg = str(e)
                error_trace = traceback.format_exc()

                logger.error(f"Error processing record: {error_msg}")
                logger.error(f"Traceback: {error_trace}")

                try:
                    message_body = json.loads(record["body"])
                    session_id = message_body.get("session_id", "unknown")
                except:
                    session_id = "unknown"

                results["failed"].append(
                    {"session_id": session_id, "error": error_msg, "trace": error_trace}
                )

                try:
                    if session_id != "unknown":
                        db.log_processing_error(
                            session_id=session_id,
                            error_type=type(e).__name__,
                            error_message=error_msg,
                            error_stack=error_trace,
                        )

                        retry_count = message_body.get("retry_count", 0)
                        if retry_count >= 3:
                            db.update_session_status(
                                session_id=session_id, status="failed"
                            )
                except Exception as db_error:
                    logger.error(f"Failed to log error to database: {db_error}")

    finally:
        db.close()

    total_processed = len(results["successful"]) + len(results["failed"])
    success_rate = (
        len(results["successful"]) / total_processed if total_processed > 0 else 0
    )

    response = {
        "statusCode": 200 if len(results["failed"]) == 0 else 207,
        "body": json.dumps(
            {
                "message": f"Processed {total_processed} messages",
                "success_rate": success_rate,
                "results": results,
            }
        ),
    }

    logger.info(f"Lambda execution completed: {response}")

    return response


def local_test():
    test_event = {
        "Records": [
            {
                "body": json.dumps(
                    {
                        "session_id": "test-session-id",
                        "s3_key": "sessions/test-audio.mp3",
                        "retry_count": 0,
                    }
                )
            }
        ]
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    local_test()
