import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Generator
from urllib.parse import urlparse
from contextlib import contextmanager
import pg8000.native

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError("DATABASE_URL not provided")

        self.database_url = database_url
        self.conn: Optional[pg8000.native.Connection] = None
        self._connect()

    def _connect(self):
        try:
            parsed = urlparse(self.database_url)

            self.conn = pg8000.native.Connection(
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:] if parsed.path else None,
            )

            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

    @contextmanager
    def get_cursor(self) -> Generator[pg8000.native.Connection, None, None]:
        if self.conn is None:
            raise RuntimeError("Database connection not established")
        try:
            yield self.conn
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self.get_cursor() as conn:
            result = conn.run(
                """
                SELECT 
                    id, therapist_id, patient_id, session_date,
                    session_duration_minutes, processing_status,
                    audio_metadata, summary, created_at
                FROM sessions
                WHERE id = :session_id AND is_deleted = FALSE
                """,
                session_id=session_id,
            )

            if result:
                logger.info(f"Retrieved session {session_id}")
                columns = [
                    "id",
                    "therapist_id",
                    "patient_id",
                    "session_date",
                    "session_duration_minutes",
                    "processing_status",
                    "audio_metadata",
                    "summary",
                    "created_at",
                ]
                return dict(zip(columns, result[0]))
            else:
                logger.warning(f"Session {session_id} not found")
                return None

    def update_session_status(
        self,
        session_id: str,
        status: str,
        processing_started_at: Optional[datetime] = None,
        processing_completed_at: Optional[datetime] = None,
    ):
        with self.get_cursor() as conn:
            update_fields = ["processing_status = :status", "updated_at = NOW()"]
            params = {"status": status, "session_id": session_id}

            if processing_started_at:
                update_fields.append("processing_started_at = :processing_started_at")
                params["processing_started_at"] = str(processing_started_at)

            if processing_completed_at:
                update_fields.append(
                    "processing_completed_at = :processing_completed_at"
                )
                params["processing_completed_at"] = str(processing_completed_at)

            query = f"""
                UPDATE sessions
                SET {', '.join(update_fields)}
                WHERE id = :session_id
            """

            conn.run(query, **params)
            logger.info(f"Updated session {session_id} status to {status}")

    def save_session_summary(
        self,
        session_id: str,
        summary: Dict[str, Any],
        tokens_used: Optional[Dict[str, int]] = None,
    ):
        if tokens_used:
            summary["tokens_used"] = tokens_used

        with self.get_cursor() as conn:
            conn.run(
                """
                UPDATE sessions
                SET 
                    summary = :summary,
                    processing_status = 'completed',
                    processing_completed_at = NOW(),
                    updated_at = NOW()
                WHERE id = :session_id
                """,
                summary=json.dumps(summary),
                session_id=session_id,
            )

            logger.info(f"Saved summary for session {session_id}")

    def log_processing_error(
        self,
        session_id: str,
        error_type: str,
        error_message: str,
        error_stack: Optional[str] = None,
        job_id: Optional[str] = None,
        retry_count: int = 0,
    ):
        import uuid

        # Provide a default job_id if none is provided (Lambda doesn't use SQS job IDs)
        if job_id is None:
            job_id = "lambda-worker"

        with self.get_cursor() as conn:
            conn.run(
                """
                INSERT INTO processing_errors (
                    id, session_id, job_id, error_type, error_message,
                    error_stack, retry_count, created_at
                )
                VALUES (:id, :session_id, :job_id, :error_type, :error_message, 
                        :error_stack, :retry_count, NOW())
                """,
                id=str(uuid.uuid4()),
                session_id=session_id,
                job_id=job_id,
                error_type=error_type,
                error_message=error_message,
                error_stack=error_stack,
                retry_count=retry_count,
            )

            logger.info(f"Logged error for session {session_id}: {error_type}")

    def create_audit_log(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        with self.get_cursor() as conn:
            conn.run(
                """
                INSERT INTO audit_logs (
                    user_id, action, resource_type, resource_id,
                    details, created_at
                )
                VALUES (:user_id, :action, :resource_type, :resource_id, 
                        :details, NOW())
                """,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
            )

            logger.info(f"Created audit log: {action} on {resource_type} {resource_id}")

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
