"""Utils module"""


def sanitize_password_str(s: str) -> str:
    if len(s) >= 2:
        return s[0] + len(s[1:-1]) * "*" + s[-1]
    else:
        return s