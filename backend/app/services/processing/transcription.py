import logging
import io
from typing import Dict, Any
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Transcription service initialized")

    def transcribe_audio(
        self, audio_content: bytes, filename: str = "audio.mp3", language: str = "pt"
    ) -> Dict[str, Any]:
        try:
            logger.info(
                f"Starting transcription for {filename} ({len(audio_content) / (1024*1024):.2f}MB)"
            )

            audio_file = io.BytesIO(audio_content)
            audio_file.name = filename

            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
            )

            text = transcript.text
            word_count = len(text.split())

            if word_count < 50:
                logger.warning(f"Transcription seems too short: {word_count} words")
                raise ValueError(
                    f"Transcription too short ({word_count} words). "
                    "Audio may be corrupted or mostly silent."
                )

            duration = getattr(transcript, "duration", None)

            result = {
                "text": text,
                "language": language,
                "duration": duration,
                "word_count": word_count,
                "char_count": len(text),
            }

            logger.info(
                f"Transcription completed: {word_count} words, "
                f"{len(text)} characters"
            )

            return result

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")

            error_msg = str(e).lower()

            if "file size" in error_msg or "too large" in error_msg:
                raise Exception(
                    "Audio file too large for Whisper API (max 25MB). "
                    "Please compress or split the audio file."
                )
            elif "invalid" in error_msg or "format" in error_msg:
                raise Exception(
                    "Invalid audio format. Supported formats: mp3, mp4, mpeg, "
                    "mpga, m4a, wav, webm"
                )
            else:
                raise Exception(f"Whisper API error: {str(e)}")

    def estimate_transcription_cost(self, duration_minutes: float) -> float:
        cost_per_minute = 0.006
        return duration_minutes * cost_per_minute

    def split_long_audio(self, audio_content: bytes, max_size_mb: int = 24) -> list:
        file_size_mb = len(audio_content) / (1024 * 1024)

        if file_size_mb <= max_size_mb:
            return [audio_content]

        raise ValueError(
            f"Audio file too large ({file_size_mb:.2f}MB). "
            f"Maximum size is {max_size_mb}MB. "
            "Please compress the audio before uploading."
        )
