from pydantic import ConfigDict, Field, BaseModel


class PostSerializer(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)
    
class PostCreateSerializer(PostSerializer):
    pass
    
class PostResponseSerializer(PostSerializer):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date_posted: str