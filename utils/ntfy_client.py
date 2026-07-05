"""
Professional ntfy wrapper.

Features:
- Multiple projects through .env config
- Token auth or username/password auth
- JSON publishing
- Priorities
- Tags
- Markdown
- Click URLs
- Icons
- Attachments by URL
- Local file uploads
- Scheduled/delayed notifications
- Action buttons
- Sequence IDs for updating notifications
- Health check
- Async-compatible helpers for Discord/Nextcord bots
- Safe send methods that never crash your bot
"""

from __future__ import annotations

import asyncio
import logging
import os
import traceback
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

import requests


logger = logging.getLogger(__name__)

TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


class NtfyPriority(Enum):
    MIN = 1
    LOW = 2
    DEFAULT = 3
    HIGH = 4
    URGENT = 5


PRIORITY_ALIASES = {
    "min": NtfyPriority.MIN,
    "minimum": NtfyPriority.MIN,
    "low": NtfyPriority.LOW,
    "default": NtfyPriority.DEFAULT,
    "normal": NtfyPriority.DEFAULT,
    "high": NtfyPriority.HIGH,
    "urgent": NtfyPriority.URGENT,
    "max": NtfyPriority.URGENT,
}


@dataclass
class NtfyConfig:
    enabled: bool
    server_url: str
    topic: str
    project_name: str = "Server"
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    timeout: int = 10
    retries: int = 1

    @classmethod
    def from_env(cls, prefix: str = "NTFY_") -> "NtfyConfig":
        """
        Reads config from environment.

        Default variables:
        NTFY_ENABLED=true
        NTFY_SERVER=http://100.125.21.90:2586
        NTFY_TOPIC=cryptolink_787963ead9ca5f80
        NTFY_TOKEN=tk_xxx
        NTFY_USERNAME=optional
        NTFY_PASSWORD=optional
        NTFY_PROJECT=CryptoLink Bot
        NTFY_TIMEOUT=10
        NTFY_RETRIES=1
        """

        enabled = os.getenv(f"{prefix}ENABLED", "false").strip().lower() in TRUE_VALUES
        server_url = os.getenv(f"{prefix}SERVER", "").strip().rstrip("/")
        topic = os.getenv(f"{prefix}TOPIC", "").strip().strip("/")
        project_name = os.getenv(f"{prefix}PROJECT", "Server").strip()

        username = os.getenv(f"{prefix}USERNAME") or os.getenv(f"{prefix}USER")
        password = os.getenv(f"{prefix}PASSWORD")
        token = os.getenv(f"{prefix}TOKEN")

        timeout = _safe_int(os.getenv(f"{prefix}TIMEOUT"), default=10)
        retries = _safe_int(os.getenv(f"{prefix}RETRIES"), default=1)

        if enabled and not server_url:
            raise RuntimeError(f"{prefix}ENABLED=true but {prefix}SERVER is missing")

        if enabled and not topic:
            raise RuntimeError(f"{prefix}ENABLED=true but {prefix}TOPIC is missing")

        return cls(
            enabled=enabled,
            server_url=server_url,
            topic=topic,
            project_name=project_name,
            username=username,
            password=password,
            token=token,
            timeout=timeout,
            retries=retries,
        )


@dataclass
class NtfyAction:
    """
    ntfy action button.

    Supported action types:
    - view: open URL/app
    - http: send HTTP request
    - copy: copy value to clipboard
    - broadcast: Android broadcast
    """

    action: str
    label: str
    url: Optional[str] = None
    value: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[Mapping[str, str]] = None
    body: Optional[str] = None
    clear: Optional[bool] = None
    intent: Optional[str] = None
    extras: Optional[Mapping[str, str]] = None

    @classmethod
    def view(cls, label: str, url: str, clear: bool = True) -> "NtfyAction":
        return cls(action="view", label=label, url=url, clear=clear)

    @classmethod
    def copy(cls, label: str, value: str, clear: bool = True) -> "NtfyAction":
        return cls(action="copy", label=label, value=value, clear=clear)

    @classmethod
    def http(
        cls,
        label: str,
        url: str,
        method: str = "POST",
        body: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        clear: bool = True,
    ) -> "NtfyAction":
        return cls(
            action="http",
            label=label,
            url=url,
            method=method.upper(),
            body=body,
            headers=headers,
            clear=clear,
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "action": self.action,
            "label": self.label,
        }

        optional_fields = {
            "url": self.url,
            "value": self.value,
            "method": self.method,
            "headers": dict(self.headers) if self.headers else None,
            "body": self.body,
            "clear": self.clear,
            "intent": self.intent,
            "extras": dict(self.extras) if self.extras else None,
        }

        for key, value in optional_fields.items():
            if value is not None:
                data[key] = value

        return data


@dataclass
class NtfyResponse:
    ok: bool
    status_code: int
    raw: Dict[str, Any]

    @property
    def id(self) -> Optional[str]:
        return self.raw.get("id")

    @property
    def topic(self) -> Optional[str]:
        return self.raw.get("topic")

    @property
    def message(self) -> Optional[str]:
        return self.raw.get("message")


class NtfyClient:
    def __init__(self, config: NtfyConfig):
        self.config = config
        self.session = requests.Session()

    @classmethod
    def from_env(cls, prefix: str = "NTFY_") -> "NtfyClient":
        return cls(NtfyConfig.from_env(prefix=prefix))

    @property
    def enabled(self) -> bool:
        return self.config.enabled

    @property
    def server_url(self) -> str:
        return self.config.server_url.rstrip("/")

    @property
    def default_topic(self) -> str:
        return self.config.topic.strip("/")

    def health(self) -> bool:
        """
        Checks ntfy server health endpoint.
        Returns True only if HTTP 200 and {"healthy": true}.
        """

        if not self.enabled:
            return False

        response = self.session.get(
            f"{self.server_url}/v1/health",
            headers=self._auth_headers(),
            timeout=self.config.timeout,
        )

        if response.status_code != 200:
            return False

        try:
            return bool(response.json().get("healthy"))
        except ValueError:
            return False

    def send(
        self,
        message: str,
        title: Optional[str] = None,
        priority: Union[NtfyPriority, str, int] = NtfyPriority.DEFAULT,
        tags: Optional[Iterable[str]] = None,
        topic: Optional[str] = None,
        markdown: bool = False,
        click: Optional[str] = None,
        icon: Optional[str] = None,
        attach: Optional[str] = None,
        filename: Optional[str] = None,
        delay: Optional[str] = None,
        actions: Optional[Sequence[Union[NtfyAction, Mapping[str, Any]]]] = None,
        email: Optional[str] = None,
        call: Optional[str] = None,
        sequence_id: Optional[str] = None,
        cache: Optional[bool] = None,
        firebase: Optional[bool] = None,
    ) -> Optional[NtfyResponse]:
        """
        Sends a notification using ntfy JSON publishing.

        Examples:
        client.send("Bot started", title="CryptoLink", priority="high", tags=["computer"])

        delay examples:
        - "30min"
        - "3h"
        - "tomorrow, 10am"

        sequence_id:
        - Use this to update an existing notification instead of creating separate visible alerts.
        """

        if not self.enabled:
            return None

        payload = self._build_payload(
            message=message,
            title=title,
            priority=priority,
            tags=tags,
            topic=topic,
            markdown=markdown,
            click=click,
            icon=icon,
            attach=attach,
            filename=filename,
            delay=delay,
            actions=actions,
            email=email,
            call=call,
            sequence_id=sequence_id,
            cache=cache,
            firebase=firebase,
        )

        return self._post_json(payload)

    def safe_send(self, *args: Any, **kwargs: Any) -> Optional[NtfyResponse]:
        """
        Sends a notification but never crashes the calling program.
        Use this in production bot code.
        """

        try:
            return self.send(*args, **kwargs)
        except Exception as exc:
            logger.warning("ntfy notification failed: %s", exc)
            return None

    async def send_async(self, *args: Any, **kwargs: Any) -> Optional[NtfyResponse]:
        """
        Async wrapper for Discord/Nextcord bots.
        """

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.send(*args, **kwargs))

    async def safe_send_async(self, *args: Any, **kwargs: Any) -> Optional[NtfyResponse]:
        try:
            return await self.send_async(*args, **kwargs)
        except Exception as exc:
            logger.warning("ntfy async notification failed: %s", exc)
            return None

    def send_file(
        self,
        file_path: Union[str, Path],
        message: str = "",
        title: Optional[str] = None,
        priority: Union[NtfyPriority, str, int] = NtfyPriority.DEFAULT,
        tags: Optional[Iterable[str]] = None,
        topic: Optional[str] = None,
        filename: Optional[str] = None,
        markdown: bool = False,
    ) -> Optional[NtfyResponse]:
        """
        Uploads a local file as an ntfy attachment.

        Your ntfy server must have attachment-cache-dir configured.
        """

        if not self.enabled:
            return None

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {path}")

        topic_value = self._resolve_topic(topic)
        url = f"{self.server_url}/{topic_value}"

        headers = self._publish_headers(
            title=title,
            priority=priority,
            tags=tags,
            filename=filename or path.name,
            markdown=markdown,
        )

        if message:
            headers["Message"] = message

        with path.open("rb") as file_obj:
            response = self._request(
                method="PUT",
                url=url,
                headers=headers,
                data=file_obj,
            )

        return self._to_ntfy_response(response)

    def send_exception(
        self,
        exc: BaseException,
        context: str = "Unhandled exception",
        priority: Union[NtfyPriority, str, int] = NtfyPriority.URGENT,
        tags: Optional[Iterable[str]] = None,
        include_traceback: bool = True,
    ) -> Optional[NtfyResponse]:
        if include_traceback:
            details = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )
            details = details[-3500:]
        else:
            details = f"{type(exc).__name__}: {exc}"

        return self.safe_send(
            title=f"{self.config.project_name} error",
            message=f"{context}\n\n{details}",
            priority=priority,
            tags=tags or ["warning"],
        )

    async def send_exception_async(
        self,
        exc: BaseException,
        context: str = "Unhandled exception",
        priority: Union[NtfyPriority, str, int] = NtfyPriority.URGENT,
        tags: Optional[Iterable[str]] = None,
        include_traceback: bool = True,
    ) -> Optional[NtfyResponse]:
        return await self.safe_send_async(
            title=f"{self.config.project_name} error",
            message=self._exception_message(exc, context, include_traceback),
            priority=priority,
            tags=tags or ["warning"],
        )

    def startup(self, message: str = "Process started.") -> Optional[NtfyResponse]:
        return self.safe_send(
            title=self.config.project_name,
            message=message,
            priority=NtfyPriority.DEFAULT,
            tags=["computer"],
        )

    def online(self, message: str = "Service is online.") -> Optional[NtfyResponse]:
        return self.safe_send(
            title=self.config.project_name,
            message=message,
            priority=NtfyPriority.HIGH,
            tags=["white_check_mark"],
        )

    def shutdown(self, message: str = "Process exited.") -> Optional[NtfyResponse]:
        return self.safe_send(
            title=self.config.project_name,
            message=message,
            priority=NtfyPriority.HIGH,
            tags=["warning"],
        )

    def _build_payload(
        self,
        message: str,
        title: Optional[str],
        priority: Union[NtfyPriority, str, int],
        tags: Optional[Iterable[str]],
        topic: Optional[str],
        markdown: bool,
        click: Optional[str],
        icon: Optional[str],
        attach: Optional[str],
        filename: Optional[str],
        delay: Optional[str],
        actions: Optional[Sequence[Union[NtfyAction, Mapping[str, Any]]]],
        email: Optional[str],
        call: Optional[str],
        sequence_id: Optional[str],
        cache: Optional[bool],
        firebase: Optional[bool],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "topic": self._resolve_topic(topic),
            "message": message,
            "title": title or self.config.project_name,
            "priority": _priority_value(priority),
        }

        if tags:
            payload["tags"] = list(tags)

        optional_fields = {
            "markdown": markdown if markdown else None,
            "click": click,
            "icon": icon,
            "attach": attach,
            "filename": filename,
            "delay": delay,
            "email": email,
            "call": call,
            "sequence_id": sequence_id,
            "cache": cache,
            "firebase": firebase,
        }

        for key, value in optional_fields.items():
            if value is not None:
                payload[key] = value

        if actions:
            payload["actions"] = [
                action.to_dict() if isinstance(action, NtfyAction) else dict(action)
                for action in actions
            ]

        return payload

    def _post_json(self, payload: Mapping[str, Any]) -> NtfyResponse:
        response = self._request(
            method="POST",
            url=f"{self.server_url}/",
            json=dict(payload),
        )
        return self._to_ntfy_response(response)

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        headers = kwargs.pop("headers", {}) or {}
        headers = {**self._auth_headers(), **headers}

        auth = None
        if not self.config.token and self.config.username and self.config.password:
            auth = (self.config.username, self.config.password)

        last_exc: Optional[BaseException] = None

        for attempt in range(self.config.retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    auth=auth,
                    timeout=self.config.timeout,
                    **kwargs,
                )

                response.raise_for_status()
                return response

            except requests.RequestException as exc:
                last_exc = exc

                if attempt >= self.config.retries:
                    raise

        raise RuntimeError(f"ntfy request failed: {last_exc}")

    def _auth_headers(self) -> Dict[str, str]:
        if self.config.token:
            return {"Authorization": f"Bearer {self.config.token}"}
        return {}

    def _publish_headers(
        self,
        title: Optional[str],
        priority: Union[NtfyPriority, str, int],
        tags: Optional[Iterable[str]],
        filename: Optional[str],
        markdown: bool,
    ) -> Dict[str, str]:
        headers = {
            "Title": title or self.config.project_name,
            "Priority": str(_priority_value(priority)),
        }

        if tags:
            headers["Tags"] = ",".join(tags)

        if filename:
            headers["Filename"] = filename

        if markdown:
            headers["Markdown"] = "yes"

        return headers

    def _resolve_topic(self, topic: Optional[str]) -> str:
        value = (topic or self.default_topic).strip().strip("/")

        if not value:
            raise ValueError("ntfy topic cannot be empty")

        return value

    def _to_ntfy_response(self, response: requests.Response) -> NtfyResponse:
        try:
            raw = response.json()
        except ValueError:
            raw = {"text": response.text}

        return NtfyResponse(
            ok=response.ok,
            status_code=response.status_code,
            raw=raw,
        )

    def _exception_message(
        self,
        exc: BaseException,
        context: str,
        include_traceback: bool,
    ) -> str:
        if include_traceback:
            details = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )
            details = details[-3500:]
        else:
            details = f"{type(exc).__name__}: {exc}"

        return f"{context}\n\n{details}"


def _priority_value(priority: Union[NtfyPriority, str, int]) -> int:
    if isinstance(priority, NtfyPriority):
        return priority.value

    if isinstance(priority, int):
        if priority not in {1, 2, 3, 4, 5}:
            raise ValueError("ntfy priority must be 1, 2, 3, 4, or 5")
        return priority

    if isinstance(priority, str):
        value = priority.strip().lower()

        if value.isdigit():
            return _priority_value(int(value))

        if value not in PRIORITY_ALIASES:
            raise ValueError(
                "Invalid ntfy priority. Use min, low, default, high, urgent, or 1-5."
            )

        return PRIORITY_ALIASES[value].value

    raise TypeError("priority must be NtfyPriority, str, or int")


def _safe_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default