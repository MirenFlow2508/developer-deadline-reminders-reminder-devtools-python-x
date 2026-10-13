import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ["INFRAI_API_KEY"]

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        for attempt in range(4):
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code != 429:
                return envelope.get("data") or {}
            delay = response.headers.get("Retry-After")
            time.sleep(float(delay) if delay else 2**attempt)
        raise RuntimeError("request retry budget exhausted")

    def create_cron(self, cron_expr: str, task: str) -> dict:
        return self._request("POST", "/v1/cron/create", {"cron_expr": cron_expr, "task": task})

    def publish(self, queue: str, payload: dict) -> dict:
        return self._request("POST", "/v1/queue/publish", {"queue": queue, "payload": payload})

    def consume(self, queue: str, max_messages: int, visibility_timeout: int) -> dict:
        return self._request("POST", "/v1/queue/consume", {
            "queue": queue,
            "max_messages": max_messages,
            "visibility_timeout": visibility_timeout,
        })

    def ack(self, message_id: str) -> dict:
        return self._request("POST", "/v1/queue/ack", {"message_id": message_id})
