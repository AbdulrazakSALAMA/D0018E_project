from pydantic import BaseModel

class CustomerInitData(BaseModel):
    user_id: int
    email: str = None
    phone_number: str = None
    name: str = None
    image_id: str = None
