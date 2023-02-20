
from jsql import sql
from domain.auth import communication, security
from domain.auth.models import LoginRequest, RegisterPendingUserRequest, ActivateUserRequest, ResendCodeRequest
from domain.user.account import get_user_profile
from domain.utils.configs import get_config
from domain.utils.enums import ConfigKey
from domain.utils.general import UserInfo, is_valid_email, is_valid_phone_number
from fastapi import Request, status, HTTPException

MAX_CODE_RESEND_ATTEMPTS = get_config(ConfigKey.MAX_VALIDATION_CODE_RESEND_ATTEMPTS)


def _validate_user_input(lang: str, *, email: str = None, phone_number: str = None):
    if email and phone_number is None:
        if not is_valid_email(email):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
            )
        return email
    elif phone_number and email is None:
        if not is_valid_phone_number(phone_number):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                
            )
        return phone_number
    else:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
        )


def _email_exists(conn, email: str):
    exists = sql(
        conn,
        """SELECT COUNT(*) FROM `user` WHERE `email` = :email""",
        email = email
    ).scalar()
    return exists > 0
    
def _phone_number_exists(conn, phone_number: str):
    exists = sql(
        conn,
        """SELECT COUNT(*) FROM `user` WHERE `phone_number` = :phone_number""",
        phone_number = phone_number
    ).scalar()
    return exists > 0


def _validate_user_password(conn, password: str, *, email: str = None, phone_number: str = None) -> bool:
    assert email or phone_number
    data = sql(
        conn,
        """
            select `password_hash`, `salt`
            from `user` u 
            where TRUE
            {% if email %}
                AND `email` = :email
            {% endif %}
            {% if phone_number %}
                AND `phone_number` = :phone_number
            {% endif %}
        """,
        email = email,
        phone_number = phone_number
    ).dict()

    if not data: return False

    return security.validate_password(
        provided_password = password,
        stored_password_hash = data["password_hash"],
        salt = data["salt"]
    )


def register_pending_user(conn, lang: str, data: RegisterPendingUserRequest):
    ##if not security.is_strong_password(data.password, data.role): 
    ##    raise HTTPException(detail = get_message(MessageCode.NOT_STRONG_PASSWORD, lang), status_code = status.HTTP_400_BAD_REQUEST)
        
    username = _validate_user_input(lang, email = data.email, phone_number = data.phone_number)

    ##if data.email and _email_exists(conn, data.email):
    ##    raise HTTPException(detail = get_message(MessageCode.EMAIL_ALREADY_EXISTS, lang), status_code = status.HTTP_400_BAD_REQUEST)
    ##if data.phone_number and _phone_number_exists(conn, data.phone_number):
    ##    raise HTTPException(detail = get_message(MessageCode.PHONE_NUMBER_ALREADY_EXISTS, lang), status_code = status.HTTP_400_BAD_REQUEST)
    

    password_hash, salt = security.hash_password_and_get_salt(data.password)
    validation_code = communication.generate_validation_code()

    pending_user_id = sql(
        conn,
        """
            INSERT INTO `pending_user`(`email_or_phone_number`, `name`, `validation_code`, `password_hash`, `salt`, `default_lang`, `role`)
            VALUES (:email_or_phone_number, :name, :validation_code, :password_hash, :salt, :default_lang, :role)
        """,
        email_or_phone_number = username,
        name = data.name,
        validation_code = validation_code,
        password_hash = password_hash,
        salt = salt,
        default_lang = lang,
        role = data.role
    ).lastrowid

    if data.email: communication.send_code_to_email(username, validation_code)
    if data.phone_number: communication.send_code_to_phone_number(username, validation_code)
    
    return pending_user_id
    
def resend_validation_code(conn, lang: str, data: ResendCodeRequest):
    username = data.email or data.phone_number
    assert username

    pending_user_info = sql(
        conn,
        """
            SELECT `validation_code`, `code_resend_attempts`
            FROM `pending_user`
            WHERE `pending_user_id` = :pending_user_id
                AND `email_or_phone_number` = :username
        """,
        username = username,
        pending_user_id = data.pending_user_id,
        attempts_limit = MAX_CODE_RESEND_ATTEMPTS
    ).dict()
    
    ##if not pending_user_info:
    ##    raise HTTPException(detail = get_message(MessageCode.USER_NOT_FOUND, lang), status_code = status.HTTP_400_BAD_REQUEST)

    validation_code, attempts = pending_user_info["validation_code"], pending_user_info["code_resend_attempts"] + 1
    
    ##if attempts > MAX_CODE_RESEND_ATTEMPTS:
    ##    raise HTTPException(detail = get_message(MessageCode.RESEND_ATTEMPTS_LIMIT, lang), status_code = status.HTTP_400_BAD_REQUEST)

    sql(
        conn,
        """
            UPDATE `pending_user`
            SET `code_resend_attempts` = :attempts
            WHERE `pending_user_id` = :pending_user_id
                AND `email_or_phone_number` = :username 
        """,
        attempts = attempts,
        pending_user_id = data.pending_user_id,
        username = username
    )

    if data.email: communication.send_code_to_email(data.email, validation_code)
    elif data.phone_number: communication.send_code_to_phone_number(data.phone_number, validation_code)

def login(conn, lang, data: LoginRequest):
    ##if not security.is_strong_password(data.password, data.role):
    ##    raise HTTPException(detail = get_message(MessageCode.NOT_STRONG_PASSWORD, lang), status_code = status.HTTP_400_BAD_REQUEST)
    
    _validate_user_input(lang, email = data.email, phone_number = data.phone_number)

    ##if not _validate_user_password(conn, data.password, email = data.email, phone_number = data.phone_number):
    ##    raise HTTPException(detail = get_message(MessageCode.INVALID_USERNAME_OR_PASSWORD, lang), status_code = status.HTTP_400_BAD_REQUEST)

    user_profile = get_user_profile(conn, email = data.email, phone_number = data.phone_number)
    access_token = security.generate_token(conn, user_profile.user_id, role = data.role)
    refresh_token = security.generate_token(conn, user_profile.user_id, role = data.role, is_refresh_token = True)
    return user_profile, access_token, refresh_token
    

def activate_user(conn, lang: str, data: ActivateUserRequest):
    assert data.role in ["customer", "manager"], "invalid-role"
    _validate_user_input(lang, email = data.email, phone_number = data.phone_number)
    pending_user = sql(
        conn,
        f"""
            SELECT *
            FROM `pending_user`
            WHERE `pending_user_id` = :pending_user_id
                AND `email_or_phone_number` = :email_or_phone_number
                AND `validation_code` = :validation_code
                AND `role` = :role
        """,
        pending_user_id = data.pending_user_id,
        validation_code = data.validation_code,
        role = data.role,
        email_or_phone_number = data.email if data.email else data.phone_number
    ).dict()

    if not pending_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST
        )

    row_count = sql(
        conn,
        f"""
            DELETE FROM `pending_user`
            WHERE `pending_user_id` = :pending_user_id
        """,
        pending_user_id = data.pending_user_id
    ).rowcount
    assert row_count == 1


    user_id = sql(
        conn,
        f"""
            INSERT INTO `user` (`email`, `phone_number`, `password_hash`, `salt`, `default_lang`, `default_role`, `name`)
            VALUES (:email, :phone_number, :password_hash, :salt, :default_lang, :role, :name)
        """,
        **pending_user,
        email = data.email,
        phone_number = data.phone_number
    ).lastrowid

    account_roles = ["customer"]
    if data.role != 'customer': account_roles.append(data.role)
    for r in account_roles:
        sql(
            conn,
            f"""
                INSERT INTO `{r}` (`user_id`)
                VALUES (:user_id)
            """,
            user_id = user_id
        )

    access_token = security.generate_token(conn, user_id, role = data.role)
    refresh_token = security.generate_token(conn, user_id, role = data.role, is_refresh_token = True)
    return access_token, refresh_token


def refresh(conn, role: str, lang: str, refresh_token: str):
    try:
        payload = security.validate_token_and_get_payload(refresh_token, conn, is_refresh_token = True)
        user_id = int(payload["id"])
        assert user_id
        return security.generate_token(conn, user_id, role = role)
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
        )

