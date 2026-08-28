import asyncio
from typing import Any
import httpx
from .config import Settings


class FocusError(RuntimeError): pass
class FocusConfigurationError(FocusError): pass
class FocusAuthenticationError(FocusError): pass
class FocusRequestError(FocusError): pass


class FocusClient:
    def __init__(self, settings: Settings):
        self.s = settings
        self._authenticated = False
        self._auth_lock = asyncio.Lock()
        headers = {}
        if settings.focus_dealer_id: headers['X-Dealer-Id'] = settings.focus_dealer_id
        if settings.focus_store_id: headers['X-Store-Id'] = settings.focus_store_id
        if settings.focus_csrf_header and settings.focus_csrf_token:
            headers[settings.focus_csrf_header] = settings.focus_csrf_token
        self.http = httpx.AsyncClient(base_url=settings.focus_base_url, headers=headers, follow_redirects=True, verify=settings.focus_verify_tls, timeout=settings.focus_timeout_seconds, limits=httpx.Limits(max_connections=settings.focus_max_connections))

    async def close(self): await self.http.aclose()

    async def authenticate(self, force: bool = False):
        if not self.s.configured: raise FocusConfigurationError('FOCUS_BASE_URL, FOCUS_USERNAME and FOCUS_PASSWORD are required')
        if self._authenticated and not force: return
        async with self._auth_lock:
            if self._authenticated and not force: return
            payload = {self.s.focus_username_field: self.s.focus_username, self.s.focus_password_field: self.s.focus_password}
            try:
                if self.s.focus_auth_mode.lower() == 'json': r = await self.http.post(self.s.focus_login_path, json=payload)
                else: r = await self.http.post(self.s.focus_login_path, data=payload)
            except httpx.HTTPError as e: raise FocusAuthenticationError(str(e)) from e
            if r.status_code >= 400: raise FocusAuthenticationError(f'FOCUS login returned HTTP {r.status_code}')
            if self.s.focus_session_cookie and self.s.focus_session_cookie not in self.http.cookies:
                raise FocusAuthenticationError('Expected FOCUS session cookie was not issued')
            self._authenticated = True

    async def request(self, method: str, path: str, **kwargs) -> Any:
        await self.authenticate()
        for attempt in range(2):
            try: r = await self.http.request(method, path, **kwargs)
            except httpx.HTTPError as e: raise FocusRequestError(str(e)) from e
            if r.status_code in (401, 403) and attempt == 0:
                self._authenticated = False
                await self.authenticate(force=True)
                continue
            if r.status_code >= 400: raise FocusRequestError(f'FOCUS returned HTTP {r.status_code}: {r.text[:500]}')
            if not r.content: return {'ok': True, 'status_code': r.status_code}
            try: return r.json()
            except ValueError: return {'ok': True, 'status_code': r.status_code, 'text': r.text}
        raise FocusRequestError('Request failed after reauthentication')

    async def health(self): return {'configured': self.s.configured, 'base_url': self.s.focus_base_url}
    async def list_workplan(self, params=None): return await self.request('GET', self.s.focus_workplan_path, params=params or {})
    async def complete_task(self, task_id, do_not_send=True, **data): return await self.request('POST', self.s.focus_workplan_complete_path.format(task_id=task_id), json={'do_not_send': do_not_send, **data})
    async def get_customer(self, customer_id): return await self.request('GET', self.s.focus_customer_path.format(customer_id=customer_id))
    async def get_notes(self, customer_id): return await self.request('GET', self.s.focus_notes_path.format(customer_id=customer_id))
    async def add_note(self, customer_id, note): return await self.request('POST', self.s.focus_notes_path.format(customer_id=customer_id), json={'note': note})
    async def send_sms(self, customer_id, message): return await self.request('POST', self.s.focus_sms_path.format(customer_id=customer_id), json={'message': message})
    async def send_email(self, customer_id, subject, body): return await self.request('POST', self.s.focus_email_path.format(customer_id=customer_id), json={'subject': subject, 'body': body})
    async def set_followup(self, customer_id, days=1, **data): return await self.request('POST', self.s.focus_followup_path.format(customer_id=customer_id), json={'days': days, **data})
    async def create_appointment(self, customer_id, **data): return await self.request('POST', self.s.focus_appointment_path.format(customer_id=customer_id), json=data)
    async def log_call(self, customer_id, outcome, note='', **data): return await self.request('POST', self.s.focus_call_log_path.format(customer_id=customer_id), json={'outcome': outcome, 'note': note, **data})
