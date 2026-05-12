from pydantic import ConfigDict, Field, BaseModel, EmailStr

class UserSerializer(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreateSerializer(UserSerializer):
    usre_id: int

class UserUpdateSerializer(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default= None, max_length=120)
    image_file: str | None = Field(default=None,min_length=1, max_length=200)
class UserResponseSerializer(UserSerializer):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str
