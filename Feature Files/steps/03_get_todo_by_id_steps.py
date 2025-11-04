import requests
from behave import given, when


BASE_URL = "http://localhost:4567"


def _resolve_placeholders(context, path: str) -> str:
    for key in ("todoId", "newTodoId"):
        if hasattr(context, key):
            path = path.replace(f"{{{key}}}", str(getattr(context, key)))
    return path


@when('I send a get-by-id GET request to "{path}"')
def step_send_get(context, path: str):
    url = f"{BASE_URL}{_resolve_placeholders(context, path)}"
    r = context.session.get(url, headers=context.headers, timeout=10)
    context.last_response = r


@when('I send a GET request to "{path}"')
def step_send_generic_get(context, path: str):
    url = f"{BASE_URL}{path}"
    r = context.session.get(url, headers=context.headers, timeout=10)
    context.last_response = r


@given('a valid todo id exists and is saved as "{var_name}"')
def step_valid_todo_saved(context, var_name):
    body = {"title": f"temp-{var_name}", "description": ""}
    r = context.session.post(f"{BASE_URL}/todos", json=body, headers=context.headers, timeout=10)
    r.raise_for_status()
    tid = str(r.json().get("id")) if r.content else None
    assert tid is not None, "Failed to create todo"
    setattr(context, var_name, tid)


@given('a new todo "{title}" is created and its id is saved as "{var_name}"')
def step_create_named_todo(context, title, var_name):
    body = {"title": title, "description": ""}
    r = context.session.post(f"{BASE_URL}/todos", json=body, headers=context.headers, timeout=10)
    r.raise_for_status()
    tid = str(r.json().get("id")) if r.content else None
    assert tid is not None, "Failed to create todo"
    setattr(context, var_name, tid)


@given("id {bad_id:d} doesn't exist")
def step_id_missing(context, bad_id: int):
    context.session.delete(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    # assure it's missing
    check = context.session.get(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    assert check.status_code == 404



