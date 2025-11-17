import logging
from datetime import datetime
from typing import Dict, Any

from .aws_clients import S3Client
from .transcription import TranscriptionService
from .summarizer import SummarizerService
from .anonymizer import PIIAnonymizer
from .database import Database

logger = logging.getLogger(__name__)


class SessionProcessor:
    def __init__(self, database: Database):
        self.db = database
        self.s3 = S3Client()
        self.transcription = TranscriptionService()
        self.summarizer = SummarizerService()
        self.anonymizer = PIIAnonymizer()

        logger.info("SessionProcessor initialized")

    def process_session(
        self, session_id: str, s3_bucket: str, s3_key: str
    ) -> Dict[str, Any]:
        logger.info(f"Starting processing for session {session_id}")
        start_time = datetime.utcnow()

        try:
            self.db.update_session_status(
                session_id=session_id,
                status="processing",
                processing_started_at=start_time,
            )

            logger.info(f"Step 1: Downloading audio from s3://{s3_bucket}/{s3_key}")
            audio_content = self.s3.download_file_stream(s3_bucket, s3_key)
            audio_metadata = self.s3.get_object_metadata(s3_bucket, s3_key)
            logger.info(f"Audio metadata: {audio_metadata}")

            logger.info("Step 2: Transcribing audio with Whisper")
            filename = s3_key.split("/")[-1]
            transcription_result = self.transcription.transcribe_audio(
                audio_content=audio_content, filename=filename, language="pt"
            )

            transcript_text = transcription_result["text"]
            logger.info(
                f"Transcription complete: {transcription_result['word_count']} words, "
                f"{transcription_result['char_count']} characters"
            )

            logger.info("Step 3: Generating summary with GPT-4o-mini")
            session_data = self.db.get_session(session_id)
            session_context = {
                "session_date": (
                    str(session_data.get("session_date")) if session_data else None
                ),
                "duration_minutes": (
                    session_data.get("session_duration_minutes")
                    if session_data
                    else None
                ),
            }

            summary = self.summarizer.generate_summary(
                transcript=transcript_text, session_context=session_context
            )

            logger.info(
                f"Summary generated with {summary.get('tokens_used', {}).get('total', 0)} tokens"
            )

            logger.info("Step 4: Anonymizing PII from summary")
            anonymized_summary = self.anonymizer.anonymize_summary(summary)

            is_clean = self.anonymizer.validate_anonymization(anonymized_summary)
            if not is_clean:
                logger.warning("PII still detected after anonymization - running again")
                anonymized_summary = self.anonymizer.anonymize_summary(
                    anonymized_summary
                )

            logger.info("Step 5: Saving summary to database")
            self.db.save_session_summary(
                session_id=session_id,
                summary=anonymized_summary,
                tokens_used=summary.get("tokens_used"),
            )

            logger.info("Step 6: Deleting audio from S3")
            deletion_success = self.s3.delete_file(s3_bucket, s3_key)

            if not deletion_success:
                logger.error(f"Failed to delete audio file s3://{s3_bucket}/{s3_key}")

            logger.info("Step 7: Finalizing session processing")
            # Note: Audit logs are created by the API for user actions, not by background workers

            end_time = datetime.utcnow()
            processing_duration = (end_time - start_time).total_seconds()

            result = {
                "status": "completed",
                "session_id": session_id,
                "processing_duration_seconds": processing_duration,
                "transcription": {
                    "word_count": transcription_result["word_count"],
                    "char_count": transcription_result["char_count"],
                },
                "summary": {
                    "main_points_count": len(anonymized_summary.get("main_points", [])),
                    "emotions_count": len(
                        anonymized_summary.get("emotions_observed", [])
                    ),
                    "action_items_count": len(
                        anonymized_summary.get("action_items", [])
                    ),
                    "risk_level": anonymized_summary.get("risk_assessment", {}).get(
                        "level"
                    ),
                    "tokens_used": summary.get("tokens_used"),
                },
                "audio_deleted": deletion_success,
            }

            logger.info(
                f"Session {session_id} processed successfully in {processing_duration:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Session processing failed: {str(e)}")

            try:
                self.db.update_session_status(session_id=session_id, status="failed")
            except Exception as db_error:
                logger.error(f"Failed to update session status: {db_error}")

            raise

    def estimate_processing_cost(
        self, audio_duration_minutes: float, estimated_word_count: int = 5000
    ) -> Dict[str, float]:
        whisper_cost = self.transcription.estimate_transcription_cost(
            audio_duration_minutes
        )

        estimated_chars = estimated_word_count * 6
        gpt_cost = self.summarizer.estimate_summary_cost(estimated_chars)
        aws_cost = 0.01

        total_cost = whisper_cost + gpt_cost + aws_cost

        return {
            "whisper_cost": whisper_cost,
            "gpt_cost": gpt_cost,
            "aws_cost": aws_cost,
            "total_cost": total_cost,
        }
