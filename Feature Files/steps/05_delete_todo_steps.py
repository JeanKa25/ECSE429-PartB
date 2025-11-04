import requests
from behave import given, when, then


BASE_URL = "http://localhost:4567"


def _resolve(context, path: str) -> str:
    for key in ("todoId", "deletedTodoId"):
        if hasattr(context, key):
            path = path.replace(f"{{{key}}}", str(getattr(context, key)))
    return path


@given("the delete server is running")
def step_server_running(context):
    context.base_url = BASE_URL
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    r = context.session.get(f"{BASE_URL}/todos", headers=context.headers, timeout=1)
    assert r.status_code == 200, ("Server not reachable")


@given("the delete system is initialized to an empty state")
def step_init_empty_state(context):
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    for endpoint, key in (("/projects", "projects"), ("/categories", "categories"), ("/todos", "todos")):
        r = context.session.get(f"{BASE_URL}{endpoint}", headers=context.headers, timeout=5)
        try:
            data = r.json()
        except Exception:
            data = {}
        items = data.get(key, []) if isinstance(data, dict) else []
        for item in items:
            item_id = item.get("id") if isinstance(item, dict) else None
            if item_id is not None:
                context.session.delete(f"{BASE_URL}{endpoint}/{item_id}", headers=context.headers, timeout=5)


@given("the following todos exist for delete:")
def step_seed_todos_delete(context):
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    context.seed_todo_ids = []
    for row in context.table:
        payload = {
            "title": row.get("title", ""),
            "doneStatus": str(row.get("doneStatus", "false")).strip().lower() in ("true", "1", "yes", "y"),
            "description": row.get("description", ""),
        }
        r = context.session.post(f"{BASE_URL}/todos", json=payload, headers=context.headers, timeout=10)
        try:
            tid = str(r.json().get("id"))
            context.seed_todo_ids.append(tid)
        except Exception:
            pass


@given('a delete todo id exists and is saved as "{var_name}"')
def step_valid_todo_saved(context, var_name):
    body = {"title": f"temp-{var_name}", "description": ""}
    r = context.session.post(f"{BASE_URL}/todos", json=body, headers=context.headers, timeout=10)
    r.raise_for_status()
    tid = str(r.json().get("id")) if r.content else None
    assert tid is not None, "Failed to create todo"
    setattr(context, var_name, tid)


@given("delete id {bad_id:d} doesn't exist")
def step_id_missing(context, bad_id: int):
    context.session.delete(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    check = context.session.get(f"{BASE_URL}/todos/{bad_id}", headers=context.headers, timeout=5)
    assert check.status_code == 404


@when('I send a delete DELETE request to "{path}"')
def step_delete_request(context, path: str):
    resolved = _resolve(context, path)
    r = context.session.delete(f"{BASE_URL}{resolved}", headers=context.headers, timeout=15)
    context.last_response = r


@then('the delete response status code should be {code:d}')
def step_assert_status(context, code: int):
    resp = getattr(context, "last_response", None)
    assert resp is not None, "No HTTP response captured"
    assert resp.status_code == code, f"Expected {code}, got {resp.status_code}. Body: {resp.text}"


