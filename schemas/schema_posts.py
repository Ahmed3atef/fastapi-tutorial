from pydantic import ConfigDict, Field, BaseModel
from datetime import datetime

from .schema_users import UserPublicSerializer


class PostSerializer(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    
class PostCreateSerializer(PostSerializer):
    user_id: int
    
    
class PostUpdateSerializer(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)
    
class PostResponseSerializer(PostSerializer):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date_posted: datetime
    author: UserPublicSerializer
    