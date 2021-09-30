from lib.utils import sanitize_password_str

def test_sanitize_password_str():
    assert sanitize_password_str("1234") == "1**4"
    assert sanitize_password_str("1") == "1"
    assert sanitize_password_str("") == ""
    assert sanitize_password_str("12") == "12"