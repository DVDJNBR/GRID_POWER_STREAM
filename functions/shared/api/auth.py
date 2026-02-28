"""
JWT Authentication — Story 4.2, Tasks 1 & 2

Azure AD JWT validation with RS256 + JWKS endpoint.
@require_auth decorator for Azure Function HTTP triggers.

AC #1: 401 on missing/invalid Authorization header.
AC #2: Token validated against Azure AD JWKS.
AC #3: 401 + descriptive message for expired/tampered tokens.
AC #4: Applied to all non-public endpoints.
"""

import functools
import json
import logging
import os
import uuid
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

try:
    import jwt as pyjwt
    from jwt.algorithms import RSAAlgorithm
    HAS_JWT = True
except ImportError:
    pyjwt = None  # type: ignore[assignment]
    HAS_JWT = False

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    _requests = None  # type: ignore[assignment]
    HAS_REQUESTS = False


# ─── Auth error ──────────────────────────────────────────────────────────────

class AuthError(Exception):
    """JWT validation failure — maps to HTTP 401."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# ─── JWT Validator ───────────────────────────────────────────────────────────

class JWTValidator:
    """
    Azure AD RS256 JWT validator.

    Fetches public keys from the Azure AD JWKS endpoint and validates:
    - Signature (RS256 via JWKS)
    - Issuer  (iss == https://login.microsoftonline.com/{tenant_id}/v2.0)
    - Audience (aud == client_id)
    - Expiration (exp) and not-before (nbf)

    Task 3.3: JWKS URI is derived from AZURE_AD_TENANT_ID env var.
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        jwks_override: Optional[dict] = None,
    ):
        """
        Args:
            tenant_id: Azure AD tenant ID (AZURE_AD_TENANT_ID).
            client_id: App Registration client ID = expected audience (AZURE_AD_CLIENT_ID).
            jwks_override: Inject JWKS directly — used in tests to avoid HTTP calls.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.jwks_uri = (
            f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        )
        self._jwks_cache: Optional[dict] = jwks_override

    def validate(self, token: str) -> dict:
        """
        Validate a Bearer token and return verified claims.

        Raises:
            AuthError: on any validation failure (expired, tampered, missing key…).
        """
        if not HAS_JWT:
            raise AuthError("PyJWT not available")

        try:
            header = pyjwt.get_unverified_header(token)  # type: ignore[union-attr]
        except pyjwt.DecodeError as exc:  # type: ignore[union-attr]
            raise AuthError(f"Malformed token: {exc}") from exc

        alg = header.get("alg", "")
        if alg != "RS256":
            raise AuthError(f"Unsupported algorithm: {alg!r} (expected RS256)")

        kid = header.get("kid")

        try:
            public_key = self._get_public_key(kid)
        except Exception as exc:
            raise AuthError(f"Cannot retrieve signing key: {exc}") from exc

        try:
            claims: dict = pyjwt.decode(  # type: ignore[union-attr]
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                options={"verify_exp": True, "verify_nbf": True, "verify_iss": True},
                issuer=self.issuer,
            )
        except pyjwt.ExpiredSignatureError as exc:  # type: ignore[union-attr]
            raise AuthError("Token has expired") from exc
        except pyjwt.InvalidAudienceError as exc:  # type: ignore[union-attr]
            raise AuthError("Invalid token audience") from exc
        except pyjwt.InvalidIssuerError as exc:  # type: ignore[union-attr]
            raise AuthError("Invalid token issuer") from exc
        except pyjwt.InvalidSignatureError as exc:  # type: ignore[union-attr]
            raise AuthError("Invalid token signature") from exc
        except pyjwt.DecodeError as exc:  # type: ignore[union-attr]
            raise AuthError(f"Token decode error: {exc}") from exc
        except pyjwt.InvalidTokenError as exc:  # type: ignore[union-attr]
            raise AuthError(f"Invalid token: {exc}") from exc

        return claims

    def _get_public_key(self, kid: Optional[str]) -> Any:
        """Fetch (and cache) JWKS; return public key matching kid."""
        if self._jwks_cache is None:
            if not HAS_REQUESTS:
                raise RuntimeError("requests not available to fetch JWKS")
            resp = _requests.get(self.jwks_uri, timeout=5)  # type: ignore[union-attr]
            resp.raise_for_status()
            self._jwks_cache = resp.json()

        jwks = self._jwks_cache
        assert jwks is not None
        keys = jwks.get("keys", [])

        # Match by kid; fallback to first key if kid is absent
        for key_data in keys:
            if kid is None or key_data.get("kid") == kid:
                return RSAAlgorithm.from_jwk(key_data)  # type: ignore[possibly-undefined]

        if keys:
            return RSAAlgorithm.from_jwk(keys[0])  # type: ignore[possibly-undefined]

        raise ValueError("No keys found in JWKS response")


# ─── Module-level validator (one instance per function host cold-start) ───────

_validator: Optional[JWTValidator] = None


def get_validator(jwks_override: Optional[dict] = None) -> JWTValidator:
    """
    Return (or create) the module-level JWTValidator.

    Task 3.2: Reads AZURE_AD_TENANT_ID + AZURE_AD_CLIENT_ID from env.
    jwks_override bypasses the JWKS HTTP call for tests.
    """
    global _validator

    if jwks_override is not None:
        # Test mode: fresh validator with injected JWKS
        return JWTValidator(
            tenant_id=os.environ.get("AZURE_AD_TENANT_ID", "test-tenant"),
            client_id=os.environ.get("AZURE_AD_CLIENT_ID", "test-client"),
            jwks_override=jwks_override,
        )

    if _validator is None:
        tenant_id = os.environ.get("AZURE_AD_TENANT_ID", "")
        client_id = os.environ.get("AZURE_AD_CLIENT_ID", "")
        if not tenant_id or not client_id:
            raise EnvironmentError(
                "AZURE_AD_TENANT_ID and AZURE_AD_CLIENT_ID must be configured"
            )
        _validator = JWTValidator(tenant_id=tenant_id, client_id=client_id)

    return _validator


def reset_validator() -> None:
    """Clear the cached validator (useful in tests that change env vars)."""
    global _validator
    _validator = None


# ─── Token extraction ─────────────────────────────────────────────────────────

def extract_bearer_token(authorization_header: str) -> Optional[str]:
    """
    Parse 'Authorization: Bearer <token>' and return the raw token.
    Returns None if the header is absent or malformed.
    """
    if not authorization_header:
        return None
    parts = authorization_header.split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


# ─── @require_auth decorator ─────────────────────────────────────────────────

def require_auth(handler: Callable) -> Callable:
    """
    Decorator that enforces Azure AD JWT authentication on HTTP trigger handlers.

    AC #1: Missing / malformed Authorization header → 401.
    AC #2: Valid token → claims extracted, handler called.
    AC #3: Expired or tampered token → 401 with descriptive message.

    Usage (inside `if AZURE_FUNCTIONS_AVAILABLE:` block):

        @app.route(route=ROUTE_PRODUCTION, methods=["GET"],
                   auth_level=func.AuthLevel.ANONYMOUS)
        @require_auth
        def get_production_regional(req: func.HttpRequest) -> func.HttpResponse:
            ...
    """
    @functools.wraps(handler)
    def wrapper(req: Any) -> Any:
        request_id = str(uuid.uuid4())

        auth_header = ""
        if hasattr(req, "headers"):
            auth_header = req.headers.get("Authorization", "")

        token = extract_bearer_token(auth_header)

        if not token:
            return _make_401(
                "Missing or invalid Authorization header — Bearer token required",
                request_id,
            )

        try:
            validator = get_validator()
            claims = validator.validate(token)
            # Attach claims for optional use by the handler
            try:
                req._auth_claims = claims  # type: ignore[attr-defined]
            except (AttributeError, TypeError):
                pass  # immutable req in some test mocks — harmless
        except EnvironmentError as exc:
            logger.error("Auth config error [%s]: %s", request_id, exc)
            return _make_401("Authentication service misconfigured", request_id)
        except AuthError as exc:
            return _make_401(exc.message, request_id)

        return handler(req)

    return wrapper


def _make_401(message: str, request_id: str) -> Any:
    """Build a 401 response — Azure Functions HttpResponse or plain _Response."""
    body = json.dumps({
        "request_id": request_id,
        "status_code": 401,
        "error": "Unauthorized",
        "message": message,
        "details": {},
    })
    headers = {
        "X-Request-Id": request_id,
        "WWW-Authenticate": 'Bearer realm="api"',
    }

    try:
        import azure.functions as func  # type: ignore[import]
        return func.HttpResponse(
            body, status_code=401, mimetype="application/json", headers=headers,
        )
    except ImportError:
        return _Response(body=body, status_code=401, headers=headers)


class _Response:
    """Lightweight response object used when azure.functions is unavailable."""

    def __init__(self, body: str, status_code: int, headers: dict):
        self._body = body
        self.status_code = status_code
        self.headers = headers
        self.mimetype = "application/json"

    def get_body(self) -> bytes:
        return self._body.encode("utf-8") if isinstance(self._body, str) else self._body
