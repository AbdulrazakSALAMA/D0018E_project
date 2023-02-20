
from domain.utils.general import UserInfo
from jsql import sql

from domain.user.models import UserProfile
from domain.utils.localization import get_message, MessageCode
from fastapi import HTTPException, status


def get_user_profile(conn, *, email: str = None, phone_number: str = None, user_info: UserInfo = None) -> UserProfile:
    if not email and not user_info and not phone_number: return None
    data = sql(
        conn,
        """
            SELECT u.`user_id`, `email`, `phone_number`, `default_lang`, `default_role`, `name`, m.url  as `image_url`
            FROM `user` u
            LEFT JOIN `image` m ON m.`image_id` = u.`image_id`
            WHERE TRUE
            {% if user_id %}
                AND u.`user_id` = :user_id
            {% endif %}
            {% if email %}
                AND `email` = :email
            {% endif %}
            {% if phone_number %}
                AND `phone_number` = :phone_number
            {% endif %}
        """,
        user_id = user_info.id,
        email = email,
        phone_number = phone_number
    ).dict()
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message(MessageCode.USER_NOT_FOUND, user_info.lang)
        )
    return UserProfile(**data)



