import os
from posixpath import join as urljoin

BOT_SERVICE_ENDPOINT_FB = os.environ.get("BOT_SERVICE_ENDPOINT_FB")
BOT_SERVICE_ENDPOINT_TG = os.environ.get("BOT_SERVICE_ENDPOINT_TG")

PUSH_TRIGGER_URLS = {
    service: urljoin(os.environ[var_name], "push")
    for service, var_name in (
        ("fb", "BOT_SERVICE_ENDPOINT_FB"),
        ("tg", "BOT_SERVICE_ENDPOINT_TG"),
    )
    if var_name in os.environ
}

REPORT_TRIGGER_URLS = {
    service: urljoin(os.environ[var_name], "report")
    for service, var_name in (
        ("fb", "BOT_SERVICE_ENDPOINT_FB"),
        ("tg", "BOT_SERVICE_ENDPOINT_TG"),
    )
    if var_name in os.environ
}

ATTACHMENT_TRIGGER_URLS = {
    service: urljoin(os.environ[var_name], "attachment")
    for service, var_name in (
        ("fb", "BOT_SERVICE_ENDPOINT_FB"),
        ("tg", "BOT_SERVICE_ENDPOINT_TG"),
    )
    if var_name in os.environ
}

MANUAL_PUSH_GROUP = os.environ.get("MANUAL_PUSH_GROUP")

DIALOGFLOW_AGENT = os.environ.get("DIALOGFLOW_AGENT")
