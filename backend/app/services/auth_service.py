from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.core.enums import ProfessionalDocType, RegisterMethod, VerificationStatus
from app.core.errors import ConflictError, ValidationError
from app.core.security import (
    generate_access_token,
    hash_password,
    mask_id_number,
    token_expire_time,
    verify_password,
)
from app.models.user import ProfessionalDocument, User, UserAuth, UserProfile
from app.repositories.token_repository import AccessTokenRecord, InMemoryTokenRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.auth import (
    AuthTokenData,
    LoginRequest,
    ProfessionalVerificationView,
    RealNameVerificationView,
    RegisterByEmailRequest,
    RegisterByPhoneRequest,
    RegisterByThirdPartyRequest,
    RegisterRequest,
    SubmitProfessionalVerificationRequest,
    SubmitRealNameVerificationRequest,
    UserAuthView,
    VerifyBasicRequest,
)


class AuthService:
    def __init__(
        self,
        user_repository: InMemoryUserRepository,
        token_repository: InMemoryTokenRepository,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository

    def register(self, request: RegisterRequest) -> tuple[User, AuthTokenData]:
        if isinstance(request, RegisterByPhoneRequest):
            user = self._register_by_phone(request)
        elif isinstance(request, RegisterByEmailRequest):
            user = self._register_by_email(request)
        else:
            user = self._register_by_third_party(request)

        token = self._issue_token(user.id)
        return user, token

    def _register_by_phone(self, request: RegisterByPhoneRequest) -> User:
        self._validate_verification_code(request.verification_code)
        if self.user_repository.find_by_phone(request.phone):
            raise ConflictError("phone already registered")

        user = User(
            register_method=RegisterMethod.PHONE,
            auth=UserAuth(
                phone=request.phone,
                phone_verified=True,
                password_hash=hash_password(request.password),
            ),
            profile=UserProfile(nickname=request.nickname),
        )
        return self.user_repository.create(user)

    def _register_by_email(self, request: RegisterByEmailRequest) -> User:
        self._validate_verification_code(request.verification_code)
        if self.user_repository.find_by_email(request.email):
            raise ConflictError("email already registered")

        user = User(
            register_method=RegisterMethod.EMAIL,
            auth=UserAuth(
                email=request.email,
                email_verified=True,
                password_hash=hash_password(request.password),
            ),
            profile=UserProfile(nickname=request.nickname),
        )
        return self.user_repository.create(user)

    def _register_by_third_party(self, request: RegisterByThirdPartyRequest) -> User:
        open_id = self._resolve_open_id(request.method, request.access_token)
        if request.method == RegisterMethod.WECHAT and self.user_repository.find_by_wechat_open_id(
            open_id
        ):
            raise ConflictError("wechat account already registered")
        if request.method == RegisterMethod.WEIBO and self.user_repository.find_by_weibo_open_id(
            open_id
        ):
            raise ConflictError("weibo account already registered")

        auth = UserAuth()
        if request.method == RegisterMethod.WECHAT:
            auth.wechat_open_id = open_id
        if request.method == RegisterMethod.WEIBO:
            auth.weibo_open_id = open_id

        user = User(
            register_method=request.method,
            auth=auth,
            profile=UserProfile(nickname=request.nickname),
        )
        return self.user_repository.create(user)

    def login(self, request: LoginRequest) -> AuthTokenData:
        user = (
            self.user_repository.find_by_phone(request.account)
            or self.user_repository.find_by_email(request.account)
            or self.user_repository.find_by_wechat_open_id(request.account)
            or self.user_repository.find_by_weibo_open_id(request.account)
        )
        if user is None:
            raise ValidationError("account or password incorrect")

        if not user.auth.password_hash:
            raise ValidationError("password login not supported for this account")

        if not verify_password(request.password, user.auth.password_hash):
            raise ValidationError("account or password incorrect")

        return self._issue_token(user.id)

    def verify_basic(self, user_id: str, request: VerifyBasicRequest) -> UserAuthView:
        user = self.user_repository.get(user_id)
        code_given = bool(request.phone_code) or bool(request.email_code)
        if not code_given:
            raise ValidationError("phone_code or email_code is required")

        if request.phone_code and user.auth.phone:
            self._validate_verification_code(request.phone_code)
            user.auth.phone_verified = True
        if request.email_code and user.auth.email:
            self._validate_verification_code(request.email_code)
            user.auth.email_verified = True

        user.touch()
        saved = self.user_repository.save(user)
        return self.to_auth_view(saved)

    def submit_real_name_verification(
        self,
        user_id: str,
        request: SubmitRealNameVerificationRequest,
    ) -> RealNameVerificationView:
        user = self.user_repository.get(user_id)
        record = user.real_name_verification
        record.status = VerificationStatus.PENDING
        record.legal_name = request.legal_name
        record.id_number = request.id_number
        record.submitted_at = datetime.now(UTC)
        record.reviewed_at = None
        record.rejection_reason = None

        # TODO: call OCR + real-name KYC provider
        pass

        if request.enable_face_recognition:
            record.face_verified = self._face_recognition_stub(
                request.face_image_url,
                request.legal_name,
                request.id_number,
            )
        else:
            record.face_verified = False

        user.touch()
        saved = self.user_repository.save(user)
        return self.to_real_name_view(saved)

    def submit_professional_verification(
        self,
        user_id: str,
        request: SubmitProfessionalVerificationRequest,
    ) -> ProfessionalVerificationView:
        user = self.user_repository.get(user_id)
        verification = user.professional_verification
        verification.documents = [
            ProfessionalDocument(
                doc_type=self._to_doc_type(doc.doc_type),
                file_name=doc.file_name,
                file_url=doc.file_url,
            )
            for doc in request.documents
        ]
        verification.status = VerificationStatus.PENDING
        verification.reviewed_at = None
        verification.rejection_reason = None
        verification.verified_by = None

        # TODO: call anti-fraud + manual audit queue service
        pass

        user.touch()
        saved = self.user_repository.save(user)
        return self.to_professional_view(saved)

    def get_user_by_token(self, token: str) -> User:
        record = self.token_repository.get(token)
        if record.expired():
            self.token_repository.revoke(token)
            raise ValidationError("token expired")
        return self.user_repository.get(record.user_id)

    def get_auth_view(self, user_id: str) -> UserAuthView:
        user = self.user_repository.get(user_id)
        return self.to_auth_view(user)

    def get_real_name_view(self, user_id: str) -> RealNameVerificationView:
        user = self.user_repository.get(user_id)
        return self.to_real_name_view(user)

    def get_professional_view(self, user_id: str) -> ProfessionalVerificationView:
        user = self.user_repository.get(user_id)
        return self.to_professional_view(user)

    def _issue_token(self, user_id: str) -> AuthTokenData:
        token = generate_access_token()
        expires_at = token_expire_time()
        self.token_repository.save(
            AccessTokenRecord(token=token, user_id=user_id, expires_at=expires_at)
        )
        return AuthTokenData(access_token=token, expires_at=expires_at)

    def _validate_verification_code(self, code: str) -> None:
        if len(code.strip()) < 4:
            raise ValidationError("verification code is invalid")
        # TODO: call sms/email verification provider
        pass

    def _resolve_open_id(self, method: RegisterMethod, access_token: str) -> str:
        if len(access_token.strip()) < 8:
            raise ValidationError("invalid third-party access token")
        # TODO: use official WeChat/Weibo OAuth API to exchange open_id
        pass

        prefix = "wx" if method == RegisterMethod.WECHAT else "wb"
        digest = hashlib.sha256(access_token.encode("utf-8")).hexdigest()[:24]
        return f"{prefix}_{digest}"

    def _face_recognition_stub(
        self,
        face_image_url: str | None,
        legal_name: str,
        id_number: str,
    ) -> bool:
        if not face_image_url:
            return False
        # TODO: integrate with face liveness and identity compare service
        pass
        return True

    def _to_doc_type(self, doc_type: str) -> ProfessionalDocType:
        mapping = {d.value: d for d in ProfessionalDocType}
        return mapping.get(doc_type, ProfessionalDocType.OTHER)

    @staticmethod
    def to_auth_view(user: User) -> UserAuthView:
        return UserAuthView(
            phone=user.auth.phone,
            phone_verified=user.auth.phone_verified,
            email=user.auth.email,
            email_verified=user.auth.email_verified,
            basic_verified=user.auth.basic_verified(),
            register_method=user.register_method,
        )

    @staticmethod
    def to_real_name_view(user: User) -> RealNameVerificationView:
        verification = user.real_name_verification
        return RealNameVerificationView(
            status=verification.status,
            legal_name=verification.legal_name,
            id_number_masked=mask_id_number(verification.id_number),
            face_verified=verification.face_verified,
            submitted_at=verification.submitted_at,
            reviewed_at=verification.reviewed_at,
            rejection_reason=verification.rejection_reason,
        )

    @staticmethod
    def to_professional_view(user: User) -> ProfessionalVerificationView:
        verification = user.professional_verification
        return ProfessionalVerificationView(
            status=verification.status,
            has_v_badge=verification.has_v_badge,
            documents=[
                {
                    "doc_type": doc.doc_type.value,
                    "file_name": doc.file_name,
                    "file_url": doc.file_url,
                    "uploaded_at": doc.uploaded_at,
                }
                for doc in verification.documents
            ],
            reviewed_at=verification.reviewed_at,
            rejection_reason=verification.rejection_reason,
        )
