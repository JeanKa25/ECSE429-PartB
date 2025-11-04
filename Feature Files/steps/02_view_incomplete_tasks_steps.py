import json
import requests
from behave import given, when, then


# Background steps
BASE_URL = "http://localhost:4567"


def _json_or_empty(resp):
    try:
        return resp.json()
    except Exception:
        return {}


def _parse_bool(val):
    return str(val).strip().lower() in ("true", "1", "yes", "y")


def _map_project_index(context, path: str) -> str:
    try:
        if path.startswith("/projects/"):
            rest = path[len("/projects/"):]
            first = rest.split("/", 1)[0]
            if first.isdigit() and hasattr(context, "seed_project_ids"):
                idx = int(first) - 1
                if 0 <= idx < len(context.seed_project_ids):
                    real = context.seed_project_ids[idx]
                    return path.replace(f"/projects/{first}/", f"/projects/{real}/", 1)
    except Exception:
        pass
    return path


@given("the following course todo lists exist for view tasks:")
def step_projects_exist_view_tasks(context):
    context.seed_project_ids = []
    for row in context.table:
        payload = {
            "title": row["title"],
            "completed": _parse_bool(row.get("completed", "false")),
            "description": row.get("description", ""),
            "active": _parse_bool(row.get("active", "true")),
        }
        r = context.session.post(f"{BASE_URL}/projects", json=payload, headers=context.headers, timeout=5)
        assert r.status_code in (200, 201), f"Create project failed: {r.status_code} {r.text}"
        try:
            context.seed_project_ids.append(str(r.json().get("id")))
        except Exception:
            pass


@given("the following todos exist for view tasks:")
def step_todos_exist_view_tasks(context):
    context.seed_todo_ids = []
    for row in context.table:
        payload = {
            "title": row["title"],
            "doneStatus": _parse_bool(row.get("doneStatus", "false")),
            "description": row.get("description", ""),
        }
        r = context.session.post(f"{BASE_URL}/todos", json=payload, headers=context.headers, timeout=5)
        assert r.status_code in (200, 201), f"Create todo failed: {r.status_code} {r.text}"
        try:
            context.seed_todo_ids.append(str(r.json().get("id")))
        except Exception:
            pass


# Generic HTTP steps used in this feature


@given('the view tasks endpoint "{endpoint}" is available')
def step_view_tasks_endpoint_available(context, endpoint):
    url = f"{BASE_URL}{_map_project_index(context, endpoint)}"
    r = context.session.get(url, headers=context.headers, timeout=5)
    context.last_response = r
    assert r.status_code < 500, f"Endpoint unavailable: {endpoint}, status={r.status_code}"


@when('I send a view tasks POST request to "{path}" with JSON body:')
def step_view_tasks_post_with_json(context, path):
    path = _map_project_index(context, path)
    payload = json.loads(context.text or "{}")
    try:
        if isinstance(payload, dict) and "id" in payload and isinstance(payload["id"], str) and payload["id"].isdigit() and hasattr(context, "seed_todo_ids"):
            idx = int(payload["id"]) - 1
            if 0 <= idx < len(context.seed_todo_ids):
                payload["id"] = context.seed_todo_ids[idx]
    except Exception:
        pass
    url = f"{BASE_URL}{path}"
    r = context.session.post(url, json=payload, headers=context.headers, timeout=10)
    context.last_response = r


@when('I send a view tasks GET request to "{path}"')
def step_view_tasks_get_request(context, path):
    path = _map_project_index(context, path)
    url = f"{BASE_URL}{path}"
    r = context.session.get(url, headers=context.headers, timeout=10)
    context.last_response = r


@then('the view tasks response status code should be {code:d}')
def step_view_tasks_assert_status_code(context, code):
    resp = getattr(context, "last_response", None)
    assert resp is not None, "No HTTP response captured"
    assert resp.status_code == code, f"Expected {code}, got {resp.status_code}. Body: {resp.text}"


@then("the view tasks response body should be an empty array")
def step_view_tasks_assert_empty_array(context):
    resp = getattr(context, "last_response", None)
    assert resp is not None, "No HTTP response captured"
    data = _json_or_empty(resp)
    # API might return [] or {"todos": []} or {"tasks": []}; treat all as empty
    if isinstance(data, list):
        assert len(data) == 0, f"Expected empty list, got: {data}"
    elif isinstance(data, dict):
        for key in ("todos", "tasks", "projects"):
            if key in data:
                assert isinstance(data[key], list) and len(data[key]) == 0, f"Expected {key}=[], got: {data}"
                return
        # If dict without a known collection key, require it to be empty
        assert len(data.keys()) == 0, f"Expected empty object, got: {data}"


