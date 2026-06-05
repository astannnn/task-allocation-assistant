from app.auth import hash_password, verify_password


def test_NFR_SEC_01_password_is_hashed_and_not_plain_text():
    """
    NFR-SEC-01:
    Passwords must not be stored in plain text.
    The stored password_hash must be different from the original password.
    """

    plain_password = "my_secure_password_123"

    password_hash = hash_password(plain_password)

    assert password_hash != plain_password
    assert plain_password not in password_hash
    assert verify_password(plain_password, password_hash) is True


def test_NFR_SEC_01_wrong_password_is_rejected():
    """
    NFR-SEC-01:
    The password verification mechanism must reject invalid passwords.
    """

    plain_password = "correct_password"
    wrong_password = "wrong_password"

    password_hash = hash_password(plain_password)

    assert verify_password(wrong_password, password_hash) is False