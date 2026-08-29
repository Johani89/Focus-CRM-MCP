from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_name: str = 'FOCUS CRM MCP'
    app_version: str = '0.1.1'
    focus_base_url: str = ''
    focus_auth_base_url: str = ''
    focus_username: str = ''
    focus_password: str = ''
    focus_dealer_id: str = ''
    focus_store_id: str = ''
    focus_auth_mode: str = 'form'
    focus_username_field: str = 'username'
    focus_password_field: str = 'password'
    focus_login_path: str = '/Account/LogOn'
    focus_session_cookie: str = ''
    focus_csrf_header: str = ''
    focus_csrf_token: str = ''
    focus_workplan_path: str = '/workplan'
    focus_workplan_complete_path: str = '/workplan/{task_id}/complete'
    focus_customer_path: str = '/customers/{customer_id}'
    focus_notes_path: str = '/customers/{customer_id}/notes'
    focus_sms_path: str = '/customers/{customer_id}/sms'
    focus_email_path: str = '/customers/{customer_id}/email'
    focus_followup_path: str = '/customers/{customer_id}/followup'
    focus_appointment_path: str = '/customers/{customer_id}/appointments'
    focus_call_log_path: str = '/customers/{customer_id}/calls'
    focus_timeout_seconds: float = 20
    focus_max_connections: int = 20
    focus_verify_tls: bool = True

    @property
    def auth_base_url(self) -> str:
        return self.focus_auth_base_url or self.focus_base_url

    @property
    def configured(self) -> bool:
        return bool(self.focus_base_url and self.auth_base_url and self.focus_username and self.focus_password)


@lru_cache
def get_settings() -> Settings:
    return Settings()
