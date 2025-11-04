import requests
from behave import when


BASE_URL = "http://localhost:4567"


@when('I send a POST request to "{path}" with raw payload:')
def step_post_raw(context, path: str):
    data = context.text or ""
    # Send raw string; keep content-type json to trigger 400 on malformed
    r = context.session.post(f"{BASE_URL}{path}", data=data, headers=context.headers, timeout=15)
    context.last_response = r


