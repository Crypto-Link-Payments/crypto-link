import asyncio
import logging
import os
import traceback
from dataclasses import dataclass
from typing import Iterable, Optional

import requests


logger = logging.getLogger(__name__)


TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass
class NtfyConfig:
    enabled: bool
    server: str
    topic: str
    username: Optional[str] = None
    password: Optional[str] = None
    project_name: str = "Server"
    timeout: int = 10

    @classmethod
    def from_env(cls) -> "NtfyConfig":
        enabled = os.getenv("NTFY_ENABLED", "false").lower() in TRUE_VALUES

        server = os.getenv("NTFY_SERVER", "").rstrip("/")
        topic = os.getenv("NTFY_TOPIC", "").strip("/")
        username = os.getenv("NTFY_USER")
        password = os.getenv("NTFY_PASSWORD")
        project_name = os.getenv("NTFY_PROJECT", "Server")

        timeout_raw = os.getenv("NTFY_TIMEOUT", "10")
        try:
            timeout = int(timeout_raw)
        except ValueError:
            timeout = 10

        if enabled and not server:
            raise RuntimeError("NTFY_ENABLED=true but NTFY_SERVER is missing")

        if enabled and not topic:
            raise RuntimeError("NTFY_ENABLED=true but NTFY_TOPIC is missing")

        return cls(
            enabled=enabled,
            server=server,
            topic=topic,
            username=username,
            password=password,
            project_name=project_name,
            timeout=timeout,
        )


class NtfyNotifier:
    def __init__(self, config: NtfyConfig):
        self.config = config

    @classmethod
    def from_env(cls) -> "NtfyNotifier":
        return cls(NtfyConfig.from_env())

    @property
    def url(self) -> str:
        return f"{self.config.server}/{self.config.topic}"

    @property
    def auth(self):
        if self.config.username and self.config.password:
            return self.config.username, self.config.password
        return None

    def send(
        self,
        message: str,
        title: Optional[str] = None,
        priority: str = "default",
        tags: Optional[Iterable[str]] = None,
        click: Optional[str] = None,
    ) -> bool:
        """
        Sends a notification synchronously.

        Priority options:
        min, low, default, high, urgent
        """

        if not self.config.enabled:
            return False

        headers = {
            "Title": title or self.config.project_name,
            "Priority": priority,
        }

        if tags:
            headers["Tags"] = ",".join(tags)

        if click:
            headers["Click"] = click

        response = requests.post(
            self.url,
            data=message.encode("utf-8"),
            headers=headers,
            auth=self.auth,
            timeout=self.config.timeout,
        )

        response.raise_for_status()
        return True

    def safe_send(
        self,
        message: str,
        title: Optional[str] = None,
        priority: str = "default",
        tags: Optional[Iterable[str]] = None,
        click: Optional[str] = None,
    ) -> bool:
        """
        Sends notification but never crashes the bot.
        Use this in production code.
        """

        try:
            return self.send(
                message=message,
                title=title,
                priority=priority,
                tags=tags,
                click=click,
            )
        except Exception as exc:
            logger.warning("Failed to send ntfy notification: %s", exc)
            return False

    async def send_async(
        self,
        message: str,
        title: Optional[str] = None,
        priority: str = "default",
        tags: Optional[Iterable[str]] = None,
        click: Optional[str] = None,
    ) -> bool:
        """
        Async wrapper compatible with Python 3.8+.
        Useful inside Discord events and commands.
        """

        loop = asyncio.get_event_loop()

        return await loop.run_in_executor(
            None,
            lambda: self.safe_send(
                message=message,
                title=title,
                priority=priority,
                tags=tags,
                click=click,
            ),
        )

    def send_exception(
        self,
        exc: Exception,
        context: str = "Unhandled exception",
        priority: str = "urgent",
    ) -> bool:
        error_text = "".join(
            traceback.format_exception_only(type(exc), exc)
        ).strip()

        message = f"{context}\n\n{error_text}"

        return self.safe_send(
            title=f"{self.config.project_name} error",
            message=message,
            priority=priority,
            tags=["warning"],
        )

    async def send_exception_async(
        self,
        exc: Exception,
        context: str = "Unhandled exception",
        priority: str = "urgent",
    ) -> bool:
        error_text = "".join(
            traceback.format_exception_only(type(exc), exc)
        ).strip()

        message = f"{context}\n\n{error_text}"

        return await self.send_async(
            title=f"{self.config.project_name} error",
            message=message,
            priority=priority,
            tags=["warning"],
        )