from dataclasses import dataclass, field
from enum import StrEnum
from typing import Annotated, Callable

from fastapi import Depends


class Event(StrEnum):
    GAMER_CREATED = "gamer_created"


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


def handle_create_gamer(notification: Notification) -> None:
    print(notification.message)


def get_notification_service() -> NotificationService:
    service = NotificationService()
    service.subscribe(Event.GAMER_CREATED, handle_create_gamer)
    return service
    

NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]
