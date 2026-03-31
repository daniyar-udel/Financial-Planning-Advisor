from __future__ import annotations

from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection
from app.logger import get_logger
from app.schemas import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.security import create_access_token, decode_access_token, hash_password, verify_password

log = get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


def register_user(payload: SignupRequest) -> TokenResponse:
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (payload.email.lower(),),
        ).fetchone()
        if existing:
            log.warning("Signup attempt for already-registered email: %s", payload.email.lower())
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        cursor = connection.execute(
            """
            INSERT INTO users (full_name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.full_name,
                payload.email.lower(),
                hash_password(payload.password),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        user_id = int(cursor.lastrowid)

    log.info("New user registered: id=%d email=%s", user_id, payload.email.lower())
    token = create_access_token(user_id, payload.email.lower())
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, full_name=payload.full_name, email=payload.email.lower()),
    )


def login_user(payload: LoginRequest) -> TokenResponse:
    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, full_name, email, password_hash FROM users WHERE email = ?",
            (payload.email.lower(),),
        ).fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        log.warning("Failed login attempt for email: %s", payload.email.lower())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    log.info("User logged in: id=%d email=%s", int(user["id"]), str(user["email"]))
    token = create_access_token(int(user["id"]), str(user["email"]))
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=int(user["id"]),
            full_name=str(user["full_name"]),
            email=str(user["email"]),
        ),
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserResponse:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from exc

    user_id = int(payload["sub"])
    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, full_name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return UserResponse(
        id=int(user["id"]),
        full_name=str(user["full_name"]),
        email=str(user["email"]),
    )
