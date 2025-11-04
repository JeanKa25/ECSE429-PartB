import json
import requests
from behave import given, when, then


BASE_URL = "http://localhost:4567"


def _resolve(context, path: str) -> str:
    for key in ("todoId",):
        if hasattr(context, key):
            path = path.replace(f"{{{key}}}", str(getattr(context, key)))
    return path


@given("the following todos exist for update:")
def step_seed_todos_update(context):
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    context.seed_todo_ids = []
    for row in context.table:
        payload = {
            "title": row.get("title", ""),
            "doneStatus": str(row.get("doneStatus", "false")).strip().lower() in ("true", "1", "yes"),
            "description": row.get("description", ""),
        }
        r = context.session.post(f"{BASE_URL}/todos", json=payload, headers=context.headers, timeout=10)
        try:
            tid = str(r.json().get("id"))
            context.seed_todo_ids.append(tid)
        except Exception:
            pass


@given('an update todo id exists and is saved as "{var_name}"')
def step_update_todo_saved(context, var_name):
    body = {"title": f"temp-{var_name}", "description": ""}
    r = context.session.post(f"{BASE_URL}/todos", json=body, headers=context.headers, timeout=10)
    r.raise_for_status()
    tid = str(r.json().get("id")) if r.content else None
    assert tid is not None, "Failed to create todo"
    setattr(context, var_name, tid)


@given("update id {bad_id:d} doesn't exist")
def step_update_id_missing(context, bad_id: int):
    context.session.delete(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    check = context.session.get(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    assert check.status_code == 404


@when('I send an update PUT request to "{path}" with JSON body:')
def step_put_with_json(context, path: str):
    payload = json.loads(context.text or "{}")
    resolved = _resolve(context, path)
    r = context.session.put(f"{BASE_URL}{resolved}", json=payload, headers=context.headers, timeout=15)
    context.last_response = r


@when('I send an update POST request to "{path}" with JSON body:')
def step_post_with_json(context, path: str):
    payload = json.loads(context.text or "{}")
    resolved = _resolve(context, path)
    r = context.session.post(f"{BASE_URL}{resolved}", json=payload, headers=context.headers, timeout=15)
    context.last_response = r


@then('the update response status code should be {code:d}')
def step_assert_status(context, code: int):
    resp = getattr(context, "last_response", None)
    assert resp is not None, "No HTTP response captured"
    assert resp.status_code == code, f"Expected {code}, got {resp.status_code}. Body: {resp.text}"


