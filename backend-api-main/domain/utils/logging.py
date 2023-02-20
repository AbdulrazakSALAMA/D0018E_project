
from domain.utils.enums import Severity


def log_message(message: str, *, severity: Severity = Severity.INFO, code: str = None):
    print(f"{message}")









