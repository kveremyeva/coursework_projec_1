from pathlib import Path

BASE_DIR = Path(__file__).parent

PATH_DATA = BASE_DIR / "data" / "operations_2025.xlsx"

JSON_DATA = BASE_DIR / "data" / "user_settings.json"

W_JSON_VIEWS = BASE_DIR / "data" / "w_json_views.json"

W_JSON_SERVICES = BASE_DIR / "data" / "w_json_services.json"

LOGS_REPORTS = BASE_DIR / "logs" / "reports.logs"

LOGS_SERVICES = BASE_DIR / "logs" / "services.logs"

LOGS_UTILS = BASE_DIR / "logs" / "utils.logs"

LOGS_VIEWS = BASE_DIR / "logs" / "views.logs"
