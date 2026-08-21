from robot_application.application import RobotApplication
from robot_application.models import Event

def test_first_entry_and_duplicate_entry():
    app = RobotApplication()

    effects = app.handle_event(Event("PERSON_ENTERED", 0, "p1"))
    assert [effect.value for effect in effects] == ["wave_hand", "欢迎光临"]

    assert app.handle_event(Event("PERSON_ENTERED", 1, "p1")) == []

def test_conversation_suppresses_greeting():
    app = RobotApplication()

    app.handle_event(Event("CONVERSATION_STARTED", 0))
    assert app.handle_event(Event("PERSON_ENTERED", 1, "p1")) == []

    app.handle_event(Event("CONVERSATION_ENDED", 2))
    assert app.handle_event(Event("PERSON_LEFT", 3, "p1")) == []

def test_farewell_after_ten_seconds_only_once():
    app = RobotApplication()

    app.handle_event(Event("PERSON_ENTERED", 0, "p1"))
    app.handle_event(Event("PERSON_LEFT", 5, "p1"))

    assert app.handle_event(Event("TICK", 14)) == []

    effects = app.handle_event(Event("TICK", 15))
    assert len(effects) == 1
    assert effects[0].value == "欢迎下次光临"

    assert app.handle_event(Event("TICK", 16)) == []

def test_return_before_timeout_does_not_farewell_or_greet_again():
    app = RobotApplication()

    app.handle_event(Event("PERSON_ENTERED", 0, "p1"))
    app.handle_event(Event("PERSON_LEFT", 5, "p1"))

    assert app.handle_event(Event("PERSON_ENTERED", 8, "p1")) == []
    assert app.handle_event(Event("TICK", 15)) == []

def test_reentry_after_confirmed_departure_is_greeted_again():
    app = RobotApplication()

    app.handle_event(Event("PERSON_ENTERED", 0, "p1"))
    app.handle_event(Event("PERSON_LEFT", 5, "p1"))
    app.handle_event(Event("TICK", 15))

    effects = app.handle_event(Event("PERSON_ENTERED", 20, "p1"))
    assert [effect.value for effect in effects] == ["wave_hand", "欢迎光临"]

def test_snapshot_isolated_from_internal_state():
    app = RobotApplication()
    app.handle_event(Event("PERSON_ENTERED", 0, "p1"))

    state = app.snapshot()
    state["left_at"]["p2"] = 100
    state["present_people"] = {"p2"}

    new_state = app.snapshot()
    assert "p2" not in new_state["left_at"]
    assert "p1" in new_state["present_people"]
