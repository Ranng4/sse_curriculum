from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import RegisterMethod, VerificationStatus


class RegisterByPhoneRequest(BaseModel):
    method: Literal[RegisterMethod.PHONE] = RegisterMethod.PHONE
    phone: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=128)
    nickname: str = Field(min_length=1, max_length=32)
    verification_code: str = Field(min_length=4, max_length=8)

    model_config = ConfigDict(use_enum_values=True)


class RegisterByEmailRequest(BaseModel):
    method: Literal[RegisterMethod.EMAIL] = RegisterMethod.EMAIL
    email: str = Field(min_length=5, max_length=128)
    password: str = Field(min_length=6, max_length=128)
    nickname: str = Field(min_length=1, max_length=32)
    verification_code: str = Field(min_length=4, max_length=8)

    model_config = ConfigDict(use_enum_values=True)


class RegisterByThirdPartyRequest(BaseModel):
    method: Literal[RegisterMethod.WECHAT, RegisterMethod.WEIBO]
    access_token: str = Field(min_length=8, max_length=512)
    nickname: str = Field(min_length=1, max_length=32)

    model_config = ConfigDict(use_enum_values=True)


RegisterRequest = Annotated[
    RegisterByPhoneRequest | RegisterByEmailRequest | RegisterByThirdPartyRequest,
    Field(discriminator="method"),
]


class LoginRequest(BaseModel):
    account: str = Field(min_length=3, max_length=128, description="phone/email/open_id")
    password: str = Field(min_length=6, max_length=128)


class VerifyBasicRequest(BaseModel):
    phone_code: str | None = Field(default=None, min_length=4, max_length=8)
    email_code: str | None = Field(default=None, min_length=4, max_length=8)

    @field_validator("phone_code", "email_code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class SubmitRealNameVerificationRequest(BaseModel):
    legal_name: str = Field(min_length=2, max_length=32)
    id_number: str = Field(min_length=8, max_length=32)
    id_front_image_url: str = Field(min_length=8, max_length=512)
    id_back_image_url: str = Field(min_length=8, max_length=512)
    face_image_url: str | None = Field(default=None, min_length=8, max_length=512)
    enable_face_recognition: bool = False


class ProfessionalDocumentInput(BaseModel):
    doc_type: str = Field(min_length=2, max_length=64)
    file_name: str = Field(min_length=1, max_length=128)
    file_url: str = Field(min_length=8, max_length=512)


class SubmitProfessionalVerificationRequest(BaseModel):
    documents: list[ProfessionalDocumentInput] = Field(min_length=1, max_length=10)


class AuthTokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


    model_config = ConfigDict(from_attributes=True)


class UserAuthView(BaseModel):
    phone: str | None = None
    phone_verified: bool = False
    email: str | None = None
    email_verified: bool = False
    basic_verified: bool = False
    register_method: RegisterMethod

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class RealNameVerificationView(BaseModel):
    status: VerificationStatus
    legal_name: str | None = None
    id_number_masked: str | None = None
    face_verified: bool = False
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class ProfessionalDocumentView(BaseModel):
    doc_type: str
    file_name: str
    file_url: str
    uploaded_at: datetime


    model_config = ConfigDict(from_attributes=True)


class ProfessionalVerificationView(BaseModel):
    status: VerificationStatus
    has_v_badge: bool = False
    documents: list[ProfessionalDocumentView]
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None

    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
