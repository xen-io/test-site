from pydantic import BaseModel


# user


class RegisterData(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class ForgotPasswordData(BaseModel):
    email: str


class ChangePasswordData(BaseModel):
    token: str
    password: str


# admin


class DeleteUserData(BaseModel):
    token: str
    id: str


class EditUserData(BaseModel):
    token: str
    id: str
    key: str
    value: str | bool | int | None


class UsersData(BaseModel):
    token: str


# from server


class StatusData(BaseModel):
    status: str
    desc: str | None = None


class TokenData(BaseModel):
    token: str
