
from jsql import sql


def is_admin(conn, user_id: int) -> bool:
    data = sql(
        conn,
        "SELECT `is_active` FROM `system_admin` WHERE `user_id` = :user_id",
        user_id = user_id
    ).dict()
    if not data or not data["is_active"]: return False
    return bool(data["is_active"])








