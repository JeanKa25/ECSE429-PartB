import requests
from behave import then


BASE_URL = "http://localhost:4567"


@then('the project should have category "{category}"')
def step_verify_project_has_category(context, category: str):
    project_id = getattr(context, "createdProjectId", None)
    if not project_id:
        # try last created by title if available
        proj = context.session.get(f"{BASE_URL}/projects", headers=context.headers, timeout=10)
        try:
            project_id = str((proj.json().get("projects", [{}])[0] or {}).get("id"))
        except Exception:
            project_id = None
    assert project_id, "No project id available to verify relationship"
    r = context.session.get(f"{BASE_URL}/projects/{project_id}/categories", headers=context.headers, timeout=10)
    assert r.status_code == 200
    try:
        cats = r.json().get("categories", [])
    except Exception:
        cats = []
    assert any(isinstance(c, dict) and c.get("title") == category for c in cats)


