
import uuid
from fastapi import HTTPException
from typing import List
from fastapi import File, UploadFile, status
from uuid import uuid4
from domain.media.models import DBImage
from domain.utils.configs import get_config
from domain.utils.enums import ConfigKey, MessageCode, UploadFileType
from domain.utils.general import TEMP_FILES_DIR, UserInfo, get_manager_info, get_worker_info
import os
from datetime import date
from jsql import sql


def delete_temp_file(remote_filename: str):
    filepath = f"{TEMP_FILES_DIR}/{remote_filename}"
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    else: return False


def validate_file_type(file: UploadFile, user_info: UserInfo, type: UploadFileType):
    if (
        (type == UploadFileType.IMAGE and file.content_type in get_config(ConfigKey.ALLOWED_IMAGE_TYPES))
         or (type == UploadFileType.VIDEO and file.content_type in get_config(ConfigKey.ALLOWED_VIDEO_TYPES))
    ):
        return True
    else:
        raise HTTPException(
            detail = get_message(MessageCode.EMAIL_ALREADY_EXISTS, user_info.lang), 
            status_code = status.HTTP_400_BAD_REQUEST
        )


def _generate_remote_filename(file: UploadFile, user_info: UserInfo) -> str:
    curr_date = date.today().strftime(f"%Y-%m-%d")
    extension = file.content_type.split("/")[-1]
    return f"{curr_date}--{user_info.id}--{uuid4()}.{extension}"


async def generate_remote_file(file: UploadFile, user_info: UserInfo, type: UploadFileType) -> str:
    validate_file_type(file, user_info, type)
    return _generate_remote_filename(file, user_info)

def get_image_url(conn, image_id: int) -> str:
    return sql(
        conn,
        """
            SELECT url
            FROM `image`
            WHERE image_id = :image_id
        """,
        image_id = image_id
    ).scalar()

# def get_images_from_db(conn, entity_id: int) -> List[DBImage]:
#     images = sql(
#         conn,
#         """
#             SELECT image_id, url, entity_id, kind
#             FROM `image`
#             WHERE entity_id = :entity_id AND kind = :kind
#         """,
#         entity_id = entity_id,
#         kind = int(kind.value)
#     ).dicts()

#     result = []
#     for image in images: result.append(DBImage(id = image["id"], url = image["url"]))
#     return result

# def get_images_count_from_db(conn):
#     return sql(
#         conn,
#         """
#             SELECT COUNT(*)
#             FROM `image`
#             WHERE entity_id = :entity_id AND kind = :kind
#         """,
#         entity_id = entity_id,
#         kind = int(kind.value)
#     ).scalar()

def insert_image_in_db(conn, user_info: UserInfo, url: str, company_id: int = None):
    
    image_id = uuid.uuid4()
    sql(
        conn,
        """
            INSERT INTO `image`(`image_id`, `user_id`, `company_id`, `url`)
            VALUES(:image_id, :user_id, :company_id, :url)
        """,
        user_id = user_info.id,
        company_id = company_id,
        url = url,
        image_id = image_id
    )

    return image_id


def insert_video_in_db(conn, user_info: UserInfo, url: str, company_id: int = None) -> str:
    video_id = uuid.uuid4()
    sql(
        conn,
        """
            INSERT INTO `video`(`video_id`, `user_id`, `company_id`, `url`)
            VALUES(:video_id, :user_id, :company_id, :url)
        """,
        user_id = user_info.id,
        company_id = company_id,
        url = url,
        video_id = video_id
    )

    return video_id


# ToDo
def _check_company_id(conn, user_info: UserInfo):
    company_id = None
    if user_info.role == "worker":
        company_id = get_worker_info(conn, user_info.id).active_company_id
    if user_info.role == "manager":
        info = get_manager_info(conn, user_info.id)
        company_id = info.company_id
    return company_id if company_id else None

def is_image_upload_allowed_for_company(conn, user_info: UserInfo) -> bool:
    return _check_company_id(conn, user_info)


def is_video_upload_allowed_for_company(conn, user_info: UserInfo) -> bool:
    return _check_company_id(conn, user_info)

