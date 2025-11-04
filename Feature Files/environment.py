import time
import requests


def _reset_system_state(session: requests.Session) -> None:
    base = "http://localhost:4567"
    headers = {"Content-Type": "application/json"}
    for endpoint, key in (("/projects", "projects"), ("/categories", "categories"), ("/todos", "todos")):
        try:
            r = session.get(f"{base}{endpoint}", headers=headers, timeout=0.1)
            try:
                data = r.json()
            except Exception:
                data = {}
            items = data.get(key, []) if isinstance(data, dict) else []
            for item in items:
                item_id = item.get("id") if isinstance(item, dict) else None
                if item_id is not None:
                    try:
                        session.delete(f"{base}{endpoint}/{item_id}", headers=headers, timeout=0.1)
                    except Exception:
                        pass
        except Exception:
            # If server is unreachable, leave cleanup to next run
            return


def before_scenario(context, scenario):
    # Ensure a session/headers and verify the server is up
    context.session = getattr(context, "session", requests.Session())
    context.headers = getattr(context, "headers", {"Content-Type": "application/json"})
    try:
        resp = context.session.get(
            "http://localhost:4567/todos",
            headers=context.headers,
            timeout=0.1,
            stream=True,
        )
        assert resp.status_code == 200, "Server not reachable on http://localhost:4567."
    except Exception:
        assert False, "Server not reachable on http://localhost:4567."


def after_scenario(context, scenario):
    # Restore default state after each test
    session = getattr(context, "session", requests.Session())
    _reset_system_state(session)


def after_step(context, step):
    # Capture created ids from POST steps
    r = getattr(context, "last_response", None)
    if not r:
        return
    try:
        body = r.json() if r.content else {}
    except Exception:
        body = {}
    req = getattr(r, "request", None)
    try:
        method = getattr(req, "method", "").upper()
        path = getattr(req, "path_url", "") or ""
    except Exception:
        method, path = "", ""
    if method == "POST" and isinstance(body, dict) and body.get("id") is not None:
        try:
            if path.startswith("/categories"):
                context.createdCategoryId = str(body.get("id"))
            elif path.startswith("/todos") and "/categories" not in path:
                context.createdTodoId = str(body.get("id"))
                # maintain list of all created todo ids in this scenario
                if not hasattr(context, "createdTodoIds") or not isinstance(context.createdTodoIds, list):
                    context.createdTodoIds = []
                context.createdTodoIds.append(context.createdTodoId)
            elif path.startswith("/projects") and "/categories" not in path:
                context.createdProjectId = str(body.get("id"))
                if not hasattr(context, "createdProjectIds") or not isinstance(context.createdProjectIds, list):
                    context.createdProjectIds = []
                context.createdProjectIds.append(context.createdProjectId)
        except Exception:
            pass

