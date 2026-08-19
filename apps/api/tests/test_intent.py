from app.services.intent import extract_intent, get_intent_state, merge_intent


def test_mercedes_request_becomes_ready_after_preferences() -> None:
    first = extract_intent("I need a 2023 Mercedes in UAE")
    update = extract_intent("C-Class under AED 180k, black, GCC specs, accident-free, under 50k km")
    state = get_intent_state(merge_intent(first, update))

    assert state.ready is True
    assert state.intent.make == "Mercedes-Benz"
    assert state.intent.budget_max == 180000
    assert state.intent.mileage_max_km == 50000


def test_missing_budget_gets_next_question() -> None:
    state = get_intent_state(extract_intent("2023 Mercedes C-Class in UAE, black GCC specs"))

    assert state.ready is False
    assert state.missing_fields == ["budget"]

