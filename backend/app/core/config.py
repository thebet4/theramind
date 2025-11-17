import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_PRESIGNED_URL_EXPIRATION: int = int(
        os.getenv("S3_PRESIGNED_URL_EXPIRATION", "900")
    )
    
    SQS_QUEUE_URL: str = os.getenv("SQS_QUEUE_URL", "")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    APP_NAME: str = os.getenv("APP_NAME", "TheraMind")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate_worker_config(self):
        required = {
            "DATABASE_URL": self.DATABASE_URL,
            "OPENAI_API_KEY": self.OPENAI_API_KEY,
            "S3_BUCKET_NAME": self.S3_BUCKET_NAME,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        logger.info("Worker configuration validated successfully")
        logger.info(f"S3 Bucket: {self.S3_BUCKET_NAME}")
        logger.info(f"AWS Region: {self.AWS_REGION}")


settings = Settings()
