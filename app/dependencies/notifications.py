from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable


class Event(StrEnum):
    SWAP_CREATED = "swap_created"
    SWAP_DUE = "swap_return_due"


@dataclass
class Notification:
    event: Event
    message: str


Handler = Callable[[Notification], None]


@dataclass
class NotificationService:
    handlers: dict[Event, list[Handler]] = field(default_factory=dict)

    def subscribe(self, event: Event, handler: Handler):
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    def unsubscribe(self, event: Event, handler: Handler):
        if event not in self.handlers:
            return
        self.handlers[event].remove(handler)

    def post(self, notification: Notification) -> None:
        if notification.event not in self.handlers:
            return
        for handler in self.handlers[notification.event]:
            handler(notification)


def handle_create_swap(notification: Notification) -> None:
    print(notification.message)


def handle_swap_due(notification: Notification) -> None:
    print(notification.message)


def get_notification_service() -> NotificationService:
    service = NotificationService()
    service.subscribe(Event.SWAP_CREATED, handle_create_swap)
    service.subscribe(Event.SWAP_DUE, handle_swap_due)
    return service
    