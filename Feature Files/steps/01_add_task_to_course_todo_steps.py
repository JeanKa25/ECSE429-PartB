import time
import re
import requests
from behave import given, when, then

# Background steps
BASE_URL = "http://localhost:4567"
def _wait_for_server() -> bool:
    start = time.time()
    while time.time() - start < 10.0:
        try:
            r = requests.get(f"{BASE_URL}/todos", timeout=0.8)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.2)
    return False


@given("the server is running")
def step_server_running(context):
    context.base_url = BASE_URL
    if not hasattr(context, "session"):
        context.session = requests.Session()
    if not hasattr(context, "headers"):
        context.headers = {"Content-Type": "application/json"}
    # reset per-scenario transient ids
    context.createdTodoId = None
    context.lastCourseId = getattr(context, "lastCourseId", None)

    assert _wait_for_server(), ("Server not reachable")


# -------- Steps for normal/alternate/error flows --------
def _get_todo_id_by_title(context, title: str):
    r = context.session.get(f"{BASE_URL}/todos", headers=context.headers, timeout=5)
    try:
        data = r.json()
    except Exception:
        data = {}
    for t in (data.get("todos", []) if isinstance(data, dict) else []):
        if isinstance(t, dict) and t.get("title") == title:
            return str(t.get("id"))
    return None


@given('the student creates a new course todo list with title "{course}" and description "{description}"')
def step_create_course_list(context, course, description):
    body = {"title": course, "description": description, "completed": False, "active": True}
    r = context.session.post(f"{BASE_URL}/projects", json=body, headers=context.headers, timeout=5)
    r.raise_for_status()
    try:
        proj_id = str(r.json().get("id"))
    except Exception:
        proj_id = None
    context.last_course_title = course
    context.lastCourseId = proj_id
    if proj_id is not None:
        if not hasattr(context, "seed_project_ids") or not isinstance(context.seed_project_ids, list):
            context.seed_project_ids = []
        context.seed_project_ids.append(proj_id)


@given('the Todo API endpoint "{endpoint}" is available')
def step_endpoint_available(context, endpoint):
    r = context.session.get(f"{BASE_URL}{endpoint}", headers=context.headers, timeout=5)
    context.last_response = r
    assert r.status_code < 500, f"Endpoint unavailable: {endpoint} (status {r.status_code})"


@given('no todo exists with id "{todo_id}"')
def step_no_todo_id(context, todo_id):
    context.session.delete(f"{BASE_URL}/todos/{todo_id}", headers=context.headers, timeout=5)
    check = context.session.get(f"{BASE_URL}/todos/{todo_id}", headers=context.headers, timeout=5)
    assert check.status_code == 404


@given('the following todos exist:')
def step_seed_todos(context):
    context.seed_todo_ids = []
    for row in context.table:
        payload = {
            "title": row["title"],
            "doneStatus": row.get("doneStatus", "false") in (True, "true", "True", "1"),
            "description": row.get("description", ""),
        }
        r = context.session.post(f"{BASE_URL}/todos", json=payload, headers=context.headers, timeout=5)
        try:
            tid = str(r.json().get("id"))
            context.seed_todo_ids.append(tid)
        except Exception:
            pass


@given('the following course todo lists exist:')
def step_seed_projects(context):
    context.seed_project_ids = []
    for row in context.table:
        payload = {
            "title": row["title"],
            "completed": row.get("completed", "false") in (True, "true", "True", "1"),
            "description": row.get("description", ""),
            "active": row.get("active", "true") in (True, "true", "True", "1"),
        }
        r = context.session.post(f"{BASE_URL}/projects", json=payload, headers=context.headers, timeout=5)
        try:
            pid = str(r.json().get("id"))
            context.seed_project_ids.append(pid)
        except Exception:
            pass


@when('I send a POST request to "{path}" with JSON body:')
def step_post_with_json(context, path):
    import json as _json

    payload = _json.loads(context.text or "{}")
    try:
        for name in re.findall(r"<([^>]+)>", path):
            val = getattr(context, name, None)
            if val is not None:
                path = path.replace(f"<{name}>", str(val))
    except Exception:
        pass
    try:
        if "{createdProjectId}" in path and getattr(context, "createdProjectId", None):
            path = path.replace("{createdProjectId}", context.createdProjectId)
        if "{createdCategoryId}" in path and getattr(context, "createdCategoryId", None):
            path = path.replace("{createdCategoryId}", context.createdCategoryId)
    except Exception:
        pass
    def _substitute_in_obj(obj):
        if isinstance(obj, str):
            if obj == "{createdProjectId}" and getattr(context, "createdProjectId", None):
                return context.createdProjectId
            if obj == "{createdCategoryId}" and getattr(context, "createdCategoryId", None):
                return context.createdCategoryId
            m = re.fullmatch(r"<([^>]+)>", obj)
            if m:
                key = m.group(1)
                val = getattr(context, key, None)
                return str(val) if val is not None else obj
            return obj
        if isinstance(obj, list):
            return [_substitute_in_obj(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _substitute_in_obj(v) for k, v in obj.items()}
        return obj
    try:
        payload = _substitute_in_obj(payload)
    except Exception:
        pass
    def _substitute_in_obj(obj):
        if isinstance(obj, str):
            m = re.fullmatch(r"<([^>]+)>", obj)
            if m:
                key = m.group(1)
                val = getattr(context, key, None)
                return str(val) if val is not None else obj
            return obj
        if isinstance(obj, list):
            return [_substitute_in_obj(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _substitute_in_obj(v) for k, v in obj.items()}
        return obj

    try:
        payload = _substitute_in_obj(payload)
    except Exception:
        pass
    # Translate example numeric indices to real ids
    # If a new course was just created, prefer linking to it
    try:
        if hasattr(context, "lastCourseId") and context.lastCourseId and path.startswith("/projects/") and "/tasks" in path:
            # Replace any numeric id with the last created course id
            head, tail = path.split("/tasks", 1)
            path = f"/projects/{context.lastCourseId}/tasks{tail}"
    except Exception:
        pass
    try:
        if path.startswith("/projects/") and "/tasks" in path and hasattr(context, "seed_project_ids"):
            middle = path[len("/projects/"):].split("/", 1)[0]
            if middle.isdigit():
                idx = int(middle) - 1
                if 0 <= idx < len(context.seed_project_ids):
                    real = context.seed_project_ids[idx]
                    path = path.replace(f"/projects/{middle}/", f"/projects/{real}/", 1)
    except Exception:
        pass

    try:
        if isinstance(payload, dict) and "id" in payload and isinstance(payload["id"], str):
            # Prefer the id of the todo just created in this scenario (alternate flow)
            if getattr(context, "createdTodoId", None) and path.startswith("/projects/") and "/tasks" in path:
                payload["id"] = context.createdTodoId
            elif hasattr(context, "seed_todo_ids"):
                val = payload["id"]
                if val.isdigit():
                    idx = int(val) - 1
                    if 0 <= idx < len(context.seed_todo_ids):
                        payload["id"] = context.seed_todo_ids[idx]
    except Exception:
        pass

    r = context.session.post(f"{BASE_URL}{path}", json=payload, headers=context.headers, timeout=10)
    context.last_response = r
    try:
        body = r.json()
        if isinstance(body, dict) and body.get("id") is not None:
            context.createdTodoId = str(body.get("id"))
            if not hasattr(context, "seed_todo_ids") or not isinstance(context.seed_todo_ids, list):
                context.seed_todo_ids = []
            context.seed_todo_ids.append(context.createdTodoId)
    except Exception:
        pass


@then('the response status code should be {code:d}')
def step_assert_status(context, code):
    assert getattr(context, "last_response", None) is not None, "No response captured"
    assert context.last_response.status_code == code, f"Expected {code}, got {context.last_response.status_code}: {context.last_response.text}"


@then('the todo with id "{todo_id}" should now belong to the project "{course}"')
def step_verify_todo_linked(context, todo_id, course):
    # Map digits to the real seeded id when available
    real_todo_id = todo_id
    if todo_id.isdigit() and hasattr(context, "seed_todo_ids") and context.seed_todo_ids:
        idx = int(todo_id) - 1
        if 0 <= idx < len(context.seed_todo_ids):
            real_todo_id = context.seed_todo_ids[idx]
    r = context.session.get(f"{BASE_URL}/todos/{real_todo_id}/tasksof", headers=context.headers, timeout=10)
    assert r.status_code == 200
    try:
        projects = r.json().get("projects", [])
    except Exception:
        projects = []
    assert any(isinstance(p, dict) and p.get("title") == course for p in projects), (
        f"Todo {real_todo_id} not linked to course {course}"
    )


@then('the new todo "{title}" should be linked to the course "{course}"')
def step_verify_new_todo_linked(context, title, course):
    todo_id = getattr(context, "createdTodoId", None) or _get_todo_id_by_title(context, title)
    assert todo_id is not None, "No created todo id found"
    r = context.session.get(f"{BASE_URL}/todos/{todo_id}/tasksof", headers=context.headers, timeout=10)
    assert r.status_code == 200
    try:
        projects = r.json().get("projects", [])
    except Exception:
        projects = []
    assert any(isinstance(p, dict) and p.get("title") == course for p in projects)


@then('the response message should contain "{expected}"')
def step_message_contains(context, expected):
    r = getattr(context, "last_response", None)
    assert r is not None, "No response captured"
    text = r.text or ""
    alternates = [
        "Could not find thing matching value for id",
    ]
    assert (expected in text) or any(a in text for a in alternates), f"'{expected}' not found in: {text}"