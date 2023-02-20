

from jsql import sql

from domain.utils.general import UserInfo
from domain.customer.models import CustomerInitData


def get_init_data(conn, user_id: int) -> CustomerInitData:
    data = sql(
        conn,
        """
            SELECT user_id, email, phone_number, name, image_id
            FROM `user`
            WHERE user_id = :user_id
        """,
        user_id = user_id
    ).dict()

    if not data: return None

    return CustomerInitData(**data)









