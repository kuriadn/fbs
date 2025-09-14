"""
FBS FastAPI Configuration

Pydantic-based configuration system for FBS FastAPI migration.
Replaces Django settings with modern configuration management.
"""

from pydantic import Field, field_validator, model_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

class FBSConfig(BaseSettings):
    """Main FBS configuration using Pydantic BaseSettings"""

    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    app_name: str = "FBS - Fayvad Business Suite"
    app_version: str = "3.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(env="SECRET_KEY", json_schema_extra={"description": "Django-compatible secret key"})

    # ============================================================================
    # DATABASE SETTINGS
    # ============================================================================
    database_url: str = Field(
        default="postgresql+asyncpg://odoo:four@One2@localhost:5432/fbs_system_db",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # ============================================================================
    # ODOO INTEGRATION SETTINGS
    # ============================================================================
    odoo_base_url: str = Field(
        default="http://localhost:8069",
        env="ODOO_BASE_URL"
    )
    odoo_timeout: int = Field(default=30, env="ODOO_TIMEOUT")
    odoo_max_retries: int = Field(default=3, env="ODOO_MAX_RETRIES")
    odoo_user: str = Field(default="odoo", env="ODOO_USER")
    odoo_password: str = Field(default="", env="ODOO_PASSWORD")

    # ============================================================================
    # AUTHENTICATION SETTINGS
    # ============================================================================
    token_expiry_hours: int = Field(default=24, env="TOKEN_EXPIRY_HOURS")
    handshake_expiry_hours: int = Field(default=24, env="HANDSHAKE_EXPIRY_HOURS")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_secret_key: str = Field(
        default="fbs-jwt-secret-key-change-in-production",
        env="JWT_SECRET_KEY",
        description="Secret key for JWT token signing"
    )
    jwt_expiry_hours: int = Field(default=24, env="JWT_EXPIRY_HOURS")

    # ============================================================================
    # CACHING SETTINGS
    # ============================================================================
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    cache_timeout: int = Field(default=300, env="CACHE_TIMEOUT")
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")

    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    enable_msme_features: bool = Field(default=True, env="ENABLE_MSME_FEATURES")
    enable_bi_features: bool = Field(default=True, env="ENABLE_BI_FEATURES")
    enable_workflow_features: bool = Field(default=True, env="ENABLE_WORKFLOW_FEATURES")
    enable_compliance_features: bool = Field(default=True, env="ENABLE_COMPLIANCE_FEATURES")
    enable_accounting_features: bool = Field(default=True, env="ENABLE_ACCOUNTING_FEATURES")
    enable_dms_features: bool = Field(default=True, env="ENABLE_DMS_FEATURES")
    enable_licensing_features: bool = Field(default=True, env="ENABLE_LICENSING_FEATURES")

    # ============================================================================
    # MODULE GENERATION SETTINGS
    # ============================================================================
    enable_module_generation: bool = Field(default=True, env="ENABLE_MODULE_GENERATION")
    module_generator_output_dir: str = Field(default="./generated_modules", env="MODULE_OUTPUT_DIR")
    module_generator_template_dir: str = Field(default="./templates", env="MODULE_TEMPLATE_DIR")
    module_generator_default_author: str = Field(default="FBS Module Generator", env="MODULE_DEFAULT_AUTHOR")
    module_generator_max_modules_per_tenant: int = Field(default=100, env="MODULE_MAX_PER_TENANT")
    module_generator_max_file_size_mb: int = Field(default=50, env="MODULE_MAX_FILE_SIZE_MB")
    module_generator_rate_limit_per_hour: int = Field(default=10, env="MODULE_RATE_LIMIT_PER_HOUR")

    # ============================================================================
    # CORS SETTINGS
    # ============================================================================
    cors_origins: str = Field(
        default="http://localhost:8000,http://localhost:3000,http://127.0.0.1:3000",
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default="*", env="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="*", env="CORS_ALLOW_HEADERS")

    # ============================================================================
    # LOGGING SETTINGS
    # ============================================================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_requests: bool = Field(default=True, env="LOG_REQUESTS")
    log_responses: bool = Field(default=False, env="LOG_RESPONSES")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # ============================================================================
    # FILE UPLOAD SETTINGS
    # ============================================================================
    max_upload_size: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    upload_path: str = Field(default="uploads", env="UPLOAD_PATH")
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx", "xls", "xlsx", "txt", "jpg", "jpeg", "png"],
        env="ALLOWED_FILE_TYPES"
    )

    # ============================================================================
    # BUSINESS LOGIC SETTINGS
    # ============================================================================
    default_solution_template: str = Field(default="standard", env="DEFAULT_SOLUTION_TEMPLATE")
    auto_install_modules: bool = Field(default=True, env="AUTO_INSTALL_MODULES")
    enable_auto_discovery: bool = Field(default=True, env="ENABLE_AUTO_DISCOVERY")

    # ============================================================================
    # RATE LIMITING SETTINGS
    # ============================================================================
    request_rate_limit: int = Field(default=1000, env="REQUEST_RATE_LIMIT")  # requests per hour
    request_burst_limit: int = Field(default=100, env="REQUEST_BURST_LIMIT")  # requests per minute

    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration as dict"""
        return {
            'url': self.database_url,
            'pool_size': self.database_pool_size,
            'max_overflow': self.database_max_overflow,
            'echo': self.database_echo,
        }

    @property
    def odoo_config(self) -> Dict[str, Any]:
        """Get Odoo configuration as dict"""
        return {
            'base_url': self.odoo_base_url,
            'timeout': self.odoo_timeout,
            'max_retries': self.odoo_max_retries,
            'user': self.odoo_user,
            'password': self.odoo_password,
        }

    @property
    def cache_config(self) -> Dict[str, Any]:
        """Get cache configuration as dict"""
        return {
            'url': self.redis_url,
            'timeout': self.cache_timeout,
            'enabled': self.cache_enabled,
        }

    # Modern Pydantic v2 configuration using ConfigDict
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
        return self.cors_origins

    @property
    def cors_methods_list(self) -> List[str]:
        """Get CORS methods as a list"""
        if isinstance(self.cors_allow_methods, str):
            if self.cors_allow_methods == "*":
                return ["*"]
            return [method.strip() for method in self.cors_allow_methods.split(',') if method.strip()]
        return self.cors_allow_methods

    @property
    def cors_headers_list(self) -> List[str]:
        """Get CORS headers as a list"""
        if isinstance(self.cors_allow_headers, str):
            if self.cors_allow_headers == "*":
                return ["*"]
            return [header.strip() for header in self.cors_allow_headers.split(',') if header.strip()]
        return self.cors_allow_headers

    @property
    def cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration as dict"""
        return {
            'allow_origins': self.cors_origins_list,
            'allow_credentials': self.cors_allow_credentials,
            'allow_methods': self.cors_methods_list,
            'allow_headers': self.cors_headers_list,
        }

# Global configuration instance
config = FBSConfig()

# Export for easy importing
__all__ = ['FBSConfig', 'config']
