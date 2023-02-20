from pydantic import BaseModel



class UploadImageResponse(BaseModel):
    image_id: int
    image_link: str


class UploadVideoResponse(BaseModel):
    video_id: int
    video_link: str

class DBImage(BaseModel):
    id: int
    url: str





