from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from importlib import import_module
from typing import Callable, Protocol


class Event(StrEnum):
    SWAP_CREATED = "swap_created"


@dataclass
class Notification:
    event: Event
    message: str


Handler = Callable[[Notification], None]


HANDLERS: defaultdict[Event, list[Handler]] = defaultdict(list)


def subscribe(event: Event, handler: Handler):
    HANDLERS[event].append(handler)


def unsubscribe(event: Event, handler: Handler):
    if event not in HANDLERS:
        return
    HANDLERS[event].remove(handler)


def post(notification: Notification) -> None:
    if notification.event not in HANDLERS:
        return
    for handler in HANDLERS[notification.event]:
        handler(notification)


def handle_create_swap(notification: Notification) -> None:
    print(notification.message)


class NotificationService(Protocol):
    @staticmethod
    def post(notification: Notification) -> None: ...


def get_notification_service() -> NotificationService:
    subscribe(Event.SWAP_CREATED, handle_create_swap)
    return import_module(__name__)
    