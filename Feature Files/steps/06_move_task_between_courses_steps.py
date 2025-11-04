import requests
from behave import given, when, then
import re


BASE_URL = "http://localhost:4567"


 


@given('the todo "{title}" is linked to the course "{course}"')
def step_link_todo_to_course(context, title: str, course: str):
    # Resolve ids by title
    proj = context.session.get(f"{BASE_URL}/projects", params={"title": course}, headers=context.headers, timeout=10)
    todo = context.session.get(f"{BASE_URL}/todos", params={"title": title}, headers=context.headers, timeout=10)
    pid = str((proj.json().get("projects", [{}])[0] or {}).get("id"))
    tid = str((todo.json().get("todos", [{}])[0] or {}).get("id"))
    r = context.session.post(f"{BASE_URL}/projects/{pid}/tasks", json={"id": tid}, headers=context.headers, timeout=10)
    context.last_response = r


@given('I resolve the course id for "{course}" as "{var_name}"')
@when('I resolve the course id for "{course}" as "{var_name}"')
@then('I resolve the course id for "{course}" as "{var_name}"')
def step_resolve_course_id(context, course: str, var_name: str):
    r = context.session.get(f"{BASE_URL}/projects", params={"title": course}, headers=context.headers, timeout=10)
    pid = str((r.json().get("projects", [{}])[0] or {}).get("id"))
    assert pid not in (None, "None", ""), f"Course not found: {course}"
    clean = var_name.strip("<>")
    setattr(context, var_name, pid)   # e.g., "<from_id>"
    setattr(context, clean, pid)      # e.g., "from_id"


@given('I resolve the todo id for "{title}" as "{var_name}"')
def step_resolve_todo_id(context, title: str, var_name: str):
    r = context.session.get(f"{BASE_URL}/todos", params={"title": title}, headers=context.headers, timeout=10)
    tid = str((r.json().get("todos", [{}])[0] or {}).get("id"))
    assert tid not in (None, "None", ""), f"Todo not found: {title}"
    clean = var_name.strip("<>")
    setattr(context, var_name, tid)
    setattr(context, clean, tid)

def _substitute_path(context, path: str) -> str:
    try:
        for name in re.findall(r"<([^>]+)>", path):
            val = getattr(context, name, None)
            if val is not None:
                path = path.replace(f"<{name}>", str(val))
    except Exception:
        pass
    return path


@when('I send a DELETE request to "{path}"')
def step_send_delete(context, path: str):
    path = _substitute_path(context, path)
    url = f"{BASE_URL}{path}"
    r = context.session.delete(url, headers=context.headers, timeout=15)
    context.last_response = r


@then('the todo "{title}" should be linked to the course "{course}"')
def step_assert_linked(context, title: str, course: str):
    # Resolve id by title
    todo = context.session.get(f"{BASE_URL}/todos", params={"title": title}, headers=context.headers, timeout=10)
    tid = str((todo.json().get("todos", [{}])[0] or {}).get("id"))
    rel = context.session.get(f"{BASE_URL}/todos/{tid}/tasksof", headers=context.headers, timeout=10)
    try:
        projects = rel.json().get("projects", [])
    except Exception:
        projects = []
    assert any(isinstance(p, dict) and p.get("title") == course for p in projects), (
        f"Todo '{title}' not linked to course '{course}'"
    )


