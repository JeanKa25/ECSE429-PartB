import json
import requests
from behave import given, when


BASE_URL = "http://localhost:4567"


@given('a mark-done todo id exists and is saved as "{var_name}"')
def step_mark_done_todo_saved(context, var_name):
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    body = {"title": f"temp-{var_name}", "description": "", "doneStatus": False}
    r = context.session.post(f"{BASE_URL}/todos", json=body, headers=context.headers, timeout=10)
    r.raise_for_status()
    tid = str(r.json().get("id")) if r.content else None
    assert tid is not None, "Failed to create todo"
    setattr(context, var_name, tid)


@given('a todo titled "{title}" exists and is saved as "{var_name}"')
def step_named_todo_saved(context, title, var_name):
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    body = {"title": title, "description": "", "doneStatus": False}
    r = context.session.post(f"{BASE_URL}/todos", json=body, headers=context.headers, timeout=10)
    r.raise_for_status()
    tid = str(r.json().get("id")) if r.content else None
    assert tid is not None, "Failed to create todo"
    setattr(context, var_name, tid)


@when('I mark the todo "{id_or_var}" as done')
def step_mark_todo_done(context, id_or_var: str):
    # Allow referencing a saved id by variable name
    todo_id = id_or_var
    if hasattr(context, id_or_var):
        todo_id = getattr(context, id_or_var)
    payload = {"doneStatus": True}
    r = context.session.post(f"{BASE_URL}/todos/{todo_id}", json=payload, headers=context.headers, timeout=15)
    context.last_response = r


@given('mark-done id {bad_id:d} doesn\'t exist')
def step_mark_done_id_missing(context, bad_id: int):
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    context.session.delete(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    check = context.session.get(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    assert check.status_code == 404


@when('I send a mark-done PUT request to "{path}" with JSON body:')
def step_mark_done_put(context, path: str):
    payload = json.loads(context.text or "{}")
    r = context.session.put(f"{BASE_URL}{path}", json=payload, headers=context.headers, timeout=15)
    context.last_response = r


@when('I send a mark-done POST request to "{path}" with JSON body:')
def step_mark_done_post(context, path: str):
    payload = json.loads(context.text or "{}")
    r = context.session.post(f"{BASE_URL}{path}", json=payload, headers=context.headers, timeout=15)
    context.last_response = r


