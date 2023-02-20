
from typing import List
from enum import Enum
from domain.utils.enums import OrderType, SupportTicketType
from pydantic import BaseModel
from datetime import datetime


class UserProfile(BaseModel):
    user_id: int
    email: str = None
    phone_number: str = None
    default_lang: str
    default_role: str
    name: str = None
    image_url: str = None
