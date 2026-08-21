from typing import Any

from .models import Effect, Event

class RobotApplication:
    def __init__(self, absence_timeout_s: float = 10.0):
        if absence_timeout_s < 0:
            raise ValueError("absence_timeout_s must be non-negative")

        self._absence_timeout_s = absence_timeout_s
        self._present_people: set[str] = set()
        self._welcomed_people: set[str] = set()
        self._left_at: dict[str, float] = {}
        self._farewelled_people: set[str] = set()

        self._conversation_active = False
        self._meeting_active = False

    def handle_event(self, event: Event) -> list[Effect]:
        person_key = self._person_key(event.person_id)

        if event.event_type == "CONVERSATION_STARTED":
            self._conversation_active = True
            return []

        if event.event_type == "CONVERSATION_ENDED":
            self._conversation_active = False
            return []

        if event.event_type == "MEETING_STARTED":
            self._meeting_active = True
            return []

        if event.event_type == "MEETING_ENDED":
            self._meeting_active = False
            return []

        if event.event_type == "PERSON_ENTERED":
            return self._handle_person_entered(person_key)

        if event.event_type == "PERSON_LEFT":
            self._handle_person_left(person_key, event.timestamp)
            return []

        if event.event_type == "TICK":
            return self._handle_tick(event.timestamp)

        raise ValueError(f"unsupported event type: {event.event_type}")

    def snapshot(self) -> dict[str, Any]:
        return {
            "present_people": frozenset(self._present_people),
            "welcomed_people": frozenset(self._welcomed_people),
            "left_at": dict(self._left_at),
            "farewelled_people": frozenset(self._farewelled_people),
            "conversation_active": self._conversation_active,
            "meeting_active": self._meeting_active,
        }

    @staticmethod
    def _person_key(person_id: str | None) -> str:
        return person_id if person_id is not None else "__anonymous__"

    def _handle_person_entered(self, person_key: str) -> list[Effect]:
        if person_key in self._present_people:
            return []

        self._present_people.add(person_key)

        # 仍处于等待离场确认期间，返回时不重复迎宾。
        if person_key in self._left_at:
            return []

        # 对话或会议期间不输出迎宾。
        if self._conversation_active or self._meeting_active:
            return []

        self._welcomed_people.add(person_key)

        return [
            Effect(
                effect_type="ROBOT_ACTION",
                value="wave_hand",
                reason="person_entered_when_idle",
            ),
            Effect(
                effect_type="SPEECH",
                value="欢迎光临",
                reason="person_entered_when_idle",
            ),
        ]

    def _handle_person_left(self, person_key: str, timestamp: float) -> None:
        self._present_people.discard(person_key)

        # 同一次离场只保留第一次离场时间。
        if person_key not in self._left_at:
            self._left_at[person_key] = timestamp

    def _handle_tick(self, timestamp: float) -> list[Effect]:
        if self._conversation_active or self._meeting_active:
            return []

        effects: list[Effect] = []

        for person_key, left_at in list(self._left_at.items()):
            if person_key in self._present_people:
                continue

            if person_key in self._farewelled_people:
                continue

            if timestamp - left_at < self._absence_timeout_s:
                continue

            effects.append(
                Effect(
                    effect_type="SPEECH",
                    value="欢迎下次光临",
                    reason="person_absent_for_timeout",
                )
            )

            self._farewelled_people.add(person_key)

            # 完成离场确认，下一次进入视为新的接待过程。
            self._left_at.pop(person_key, None)
            self._welcomed_people.discard(person_key)

        return effects
