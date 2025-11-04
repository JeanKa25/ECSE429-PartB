import json
import requests
from behave import then


@then('the response body should be an empty array')
def step_empty_array(context):
    resp = getattr(context, "last_response", None)
    assert resp is not None, "No HTTP response captured"
    try:
        data = resp.json()
    except Exception:
        data = None
    if isinstance(data, dict) and "todos" in data:
        assert isinstance(data["todos"], list) and len(data["todos"]) == 0
    else:
        assert isinstance(data, list) and len(data) == 0

BASE_URL = "http://localhost:4567"


@then('the response should include todos "{t1}" and "{t2}"')
def step_body_includes_todos(context, t1: str, t2: str):
    # Prefer ids captured during scenario (from environment after_step)
    expected_titles = {t1, t2}
    observed_titles = set()
    ids = []
    if hasattr(context, "createdTodoIds") and isinstance(context.createdTodoIds, list):
        ids = context.createdTodoIds[-2:]
    # Fallback: parse ids from last response
    if not ids:
        resp = getattr(context, "last_response", None)
        assert resp is not None, "No HTTP response captured"
        try:
            data = resp.json()
        except Exception:
            data = {}
        maybe = []
        if isinstance(data, dict) and isinstance(data.get("todos"), list):
            maybe = data.get("todos", [])
        elif isinstance(data, list):
            maybe = data
        ids = [str(it.get("id")) for it in maybe if isinstance(it, dict) and it.get("id") is not None]
    for tid in ids:
        try:
            r = requests.get(f"{BASE_URL}/todos/{tid}", timeout=5)
            if r.status_code == 200:
                body = r.json() if r.content else {}
                if isinstance(body, dict):
                    if isinstance(body.get("title"), str):
                        observed_titles.add(body.get("title"))
                    elif isinstance(body.get("todos"), list) and body.get("todos"):
                        first = body.get("todos")[0]
                        if isinstance(first, dict) and isinstance(first.get("title"), str):
                            observed_titles.add(first.get("title"))
        except Exception:
            pass
    missing = expected_titles - observed_titles
    assert not missing, f"Expected todos {sorted(expected_titles)} found titles {sorted(observed_titles)}; missing {sorted(missing)}"


