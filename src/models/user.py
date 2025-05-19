from pydantic import BaseModel, EmailStr


class UserInput(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserDB(UserInput):
    id: int


class ListUserResponse(BaseModel):
    users: list[UserResponse]


class Message(BaseModel):
    message: str
