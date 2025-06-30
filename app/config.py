"""Application configuration."""
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MedAI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "development-secret-key"
    database_url: str = "sqlite:///./test.db"
    cors_origins: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()

def get_settings():
    return settings

# Validadores
def validate_database_url(url: str) -> bool:
    if not url:
        return False
    return any(url.startswith(prefix) for prefix in ["postgresql://", "mysql://", "sqlite://"])

def validate_secret_key(key: str) -> bool:
    return key and len(key) >= 32

# Classes de configuração
class DatabaseConfig:
    def __init__(self, url: str, **kwargs):
        self.url = url
        self.pool_size = kwargs.get("pool_size", 5)
        self.max_overflow = kwargs.get("max_overflow", 10)
        self.pool_timeout = kwargs.get("pool_timeout", 30)
        self.echo = kwargs.get("echo", False)
        self.check_same_thread = kwargs.get("check_same_thread", False)

class SecurityConfig:
    def __init__(self, **kwargs):
        self.secret_key = kwargs.get("secret_key", "default-secret-key")
        self.algorithm = kwargs.get("algorithm", "HS256")
        self.access_token_expire_minutes = kwargs.get("access_token_expire_minutes", 30)
        self.refresh_token_expire_days = kwargs.get("refresh_token_expire_days", 7)
        self.password_min_length = kwargs.get("password_min_length", 8)
        self.password_require_uppercase = kwargs.get("password_require_uppercase", True)
        self.password_require_numbers = kwargs.get("password_require_numbers", True)
        self.password_require_special = kwargs.get("password_require_special", True)
        self.bcrypt_rounds = kwargs.get("bcrypt_rounds", 12)
        self.rate_limit_enabled = kwargs.get("rate_limit_enabled", True)
        self.rate_limit_requests = kwargs.get("rate_limit_requests", 100)
        self.rate_limit_window = kwargs.get("rate_limit_window", 60)
        self.rate_limit_burst = kwargs.get("rate_limit_burst", 10)

class MLConfig:
    def __init__(self, **kwargs):
        self.model_path = kwargs.get("model_path", "./models")
        self.model_version = kwargs.get("model_version", "latest")
        self.batch_size = kwargs.get("batch_size", 32)
        self.max_sequence_length = kwargs.get("max_sequence_length", 512)
        self.confidence_threshold = kwargs.get("confidence_threshold", 0.7)
        self.use_gpu = kwargs.get("use_gpu", False)
        self.gpu_device_id = kwargs.get("gpu_device_id", 0)
        self.diagnostic_model = kwargs.get("diagnostic_model", "default")
        self.risk_assessment_model = kwargs.get("risk_assessment_model", "default")
        self.image_analysis_model = kwargs.get("image_analysis_model", "default")
        self.nlp_model = kwargs.get("nlp_model", "default")
        self.normalize_inputs = kwargs.get("normalize_inputs", True)
        self.remove_outliers = kwargs.get("remove_outliers", True)
        self.outlier_threshold = kwargs.get("outlier_threshold", 3.0)
        self.missing_value_strategy = kwargs.get("missing_value_strategy", "mean")
        self.feature_scaling = kwargs.get("feature_scaling", "standard")

class EmailConfig:
    def __init__(self, **kwargs):
        self.smtp_host = kwargs.get("smtp_host", "localhost")
        self.smtp_port = kwargs.get("smtp_port", 587)
        self.smtp_user = kwargs.get("smtp_user", "")
        self.smtp_password = kwargs.get("smtp_password", "")
        self.use_tls = kwargs.get("use_tls", True)
        self.from_email = kwargs.get("from_email", "noreply@medai.com")
        self.template_dir = kwargs.get("template_dir", "./templates")
        self.welcome_template = kwargs.get("welcome_template", "welcome.html")
        self.password_reset_template = kwargs.get("password_reset_template", "reset.html")
        self.diagnostic_report_template = kwargs.get("diagnostic_report_template", "report.html")

class StorageConfig:
    def __init__(self, **kwargs):
        self.storage_type = kwargs.get("storage_type", "local")
        self.local_path = kwargs.get("local_path", "./uploads")
        self.max_file_size = kwargs.get("max_file_size", 10485760)
        self.allowed_extensions = kwargs.get("allowed_extensions", [".pdf", ".jpg", ".png"])
        self.s3_bucket = kwargs.get("s3_bucket", "")
        self.s3_region = kwargs.get("s3_region", "us-east-1")
        self.s3_access_key = kwargs.get("s3_access_key", "")
        self.s3_secret_key = kwargs.get("s3_secret_key", "")
        self.s3_endpoint_url = kwargs.get("s3_endpoint_url", "")
        self.organize_by_date = kwargs.get("organize_by_date", True)
        self.organize_by_type = kwargs.get("organize_by_type", True)
        self.date_format = kwargs.get("date_format", "%Y/%m/%d")
        self.create_thumbnails = kwargs.get("create_thumbnails", True)
        self.thumbnail_sizes = kwargs.get("thumbnail_sizes", [(150, 150)])

def load_environment_config():
    """Carrega configuração baseada no ambiente."""
    import os
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": {
            "debug": True,
            "log_level": "DEBUG",
            "database_url": "sqlite:///./dev.db"
        },
        "production": {
            "debug": False,
            "log_level": "INFO",
            "use_https": True
        },
        "testing": {
            "testing": True,
            "database_url": "sqlite:///:memory:"
        }
    }
    
    return configs.get(env, configs["development"])
