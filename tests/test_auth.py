"""
Tests for Story 4.2 — Azure AD / JWT Security Implementation

Tasks: 4.1 (auth.py unit), 4.2 (@require_auth decorator), 4.3 (integration flow).
"""

import json
import os
import time
import uuid
from typing import Any
from unittest.mock import patch

import pytest

# ─── RSA key fixtures (generated once per session) ───────────────────────────

@pytest.fixture(scope="session")
def rsa_keys():
    """
    Generate a test RSA-2048 key pair and build a matching JWKS dict.
    Returns (private_key, public_key, jwks).
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from jwt.algorithms import RSAAlgorithm

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    public_key = private_key.public_key()

    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk["kid"] = "test-kid-001"
    jwk["use"] = "sig"
    jwk["alg"] = "RS256"

    jwks = {"keys": [jwk]}
    return private_key, public_key, jwks


@pytest.fixture(scope="session")
def tenant_id():
    return "aaaaaaaa-0000-0000-0000-000000000000"


@pytest.fixture(scope="session")
def client_id():
    return "bbbbbbbb-1111-1111-1111-111111111111"


def _make_token(
    private_key,
    tenant_id: str,
    client_id: str,
    *,
    exp_offset: int = 3600,
    nbf_offset: int = -5,
    kid: str = "test-kid-001",
    aud_override: str | None = None,
    iss_override: str | None = None,
    extra_claims: dict | None = None,
    algorithm: str = "RS256",
) -> str:
    """Build a JWT signed with the test RSA key."""
    import jwt as pyjwt

    now = int(time.time())
    payload: dict = {
        "sub": "user-sub-001",
        "oid": "user-oid-001",
        "roles": ["DataReader"],
        "iss": iss_override or f"https://login.microsoftonline.com/{tenant_id}/v2.0",
        "aud": aud_override or client_id,
        "exp": now + exp_offset,
        "nbf": now + nbf_offset,
        "iat": now,
        "tid": tenant_id,
    }
    if extra_claims:
        payload.update(extra_claims)

    headers = {"kid": kid, "alg": algorithm}
    return pyjwt.encode(payload, private_key, algorithm=algorithm, headers=headers)


# ─── JWTValidator unit tests ─────────────────────────────────────────────────

class TestJWTValidator:

    def test_valid_token_returns_claims(self, rsa_keys, tenant_id, client_id):
        """AC #2: Valid token → claims returned."""
        from functions.shared.api.auth import JWTValidator

        priv, _, jwks = rsa_keys
        token = _make_token(priv, tenant_id, client_id)

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        claims = validator.validate(token)

        assert claims["sub"] == "user-sub-001"
        assert claims["oid"] == "user-oid-001"
        assert "DataReader" in claims["roles"]

    def test_expired_token_raises(self, rsa_keys, tenant_id, client_id):
        """AC #3: Expired token → AuthError."""
        from functions.shared.api.auth import JWTValidator, AuthError

        priv, _, jwks = rsa_keys
        token = _make_token(priv, tenant_id, client_id, exp_offset=-1)

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        with pytest.raises(AuthError, match="expired"):
            validator.validate(token)

    def test_wrong_audience_raises(self, rsa_keys, tenant_id, client_id):
        """AC #3: Wrong audience → AuthError."""
        from functions.shared.api.auth import JWTValidator, AuthError

        priv, _, jwks = rsa_keys
        token = _make_token(priv, tenant_id, client_id, aud_override="wrong-client")

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        with pytest.raises(AuthError, match="audience"):
            validator.validate(token)

    def test_wrong_issuer_raises(self, rsa_keys, tenant_id, client_id):
        """AC #3: Wrong issuer → AuthError."""
        from functions.shared.api.auth import JWTValidator, AuthError

        priv, _, jwks = rsa_keys
        token = _make_token(
            priv, tenant_id, client_id,
            iss_override="https://evil.example.com/",
        )

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        with pytest.raises(AuthError, match="[Ii]ssuer"):
            validator.validate(token)

    def test_tampered_signature_raises(self, rsa_keys, tenant_id, client_id):
        """AC #3: Tampered payload → AuthError (invalid signature)."""
        from functions.shared.api.auth import JWTValidator, AuthError
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        # Sign with a different (unknown) private key
        other_key = rsa.generate_private_key(65537, 2048, default_backend())
        priv, _, jwks = rsa_keys
        token = _make_token(other_key, tenant_id, client_id)

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        with pytest.raises(AuthError):
            validator.validate(token)

    def test_malformed_token_raises(self, rsa_keys, tenant_id, client_id):
        """AC #3: Gibberish token → AuthError."""
        from functions.shared.api.auth import JWTValidator, AuthError

        _, _, jwks = rsa_keys
        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)

        with pytest.raises(AuthError, match="[Mm]alformed"):
            validator.validate("this.is.not.a.jwt")

    def test_unsupported_algorithm_raises(self, rsa_keys, tenant_id, client_id):
        """Only RS256 is accepted."""
        from functions.shared.api.auth import JWTValidator, AuthError
        import jwt as pyjwt

        _, _, jwks = rsa_keys
        # HS256 token
        payload = {"sub": "x", "aud": client_id, "exp": int(time.time()) + 3600}
        token = pyjwt.encode(payload, "secret", algorithm="HS256")

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        with pytest.raises(AuthError, match="[Aa]lgorithm"):
            validator.validate(token)

    def test_no_matching_kid_falls_back_to_first_key(self, rsa_keys, tenant_id, client_id):
        """Validator falls back to first JWKS key when kid is absent from header."""
        import jwt as pyjwt
        from functions.shared.api.auth import JWTValidator

        priv, _, jwks = rsa_keys
        # Build token without kid header
        now = int(time.time())
        payload = {
            "sub": "u", "aud": client_id, "exp": now + 3600, "nbf": now - 5, "iat": now,
            "iss": f"https://login.microsoftonline.com/{tenant_id}/v2.0",
        }
        token = pyjwt.encode(payload, priv, algorithm="RS256")  # no headers kwarg → no kid

        validator = JWTValidator(tenant_id, client_id, jwks_override=jwks)
        claims = validator.validate(token)
        assert claims["sub"] == "u"


# ─── Task 4.1: extract_bearer_token ──────────────────────────────────────────

class TestExtractBearerToken:
    def test_valid_bearer(self):
        from functions.shared.api.auth import extract_bearer_token
        assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"

    def test_case_insensitive(self):
        from functions.shared.api.auth import extract_bearer_token
        assert extract_bearer_token("BEARER mytoken") == "mytoken"

    def test_empty_header(self):
        from functions.shared.api.auth import extract_bearer_token
        assert extract_bearer_token("") is None

    def test_missing_token(self):
        from functions.shared.api.auth import extract_bearer_token
        assert extract_bearer_token("Bearer") is None

    def test_non_bearer_scheme(self):
        from functions.shared.api.auth import extract_bearer_token
        assert extract_bearer_token("Basic dXNlcjpwYXNz") is None

    def test_none_like_empty(self):
        from functions.shared.api.auth import extract_bearer_token
        assert extract_bearer_token("") is None


# ─── Task 4.2: @require_auth decorator ───────────────────────────────────────

class MockRequest:
    """Minimal mock for func.HttpRequest."""

    def __init__(self, headers: dict | None = None, params: dict | None = None):
        self.headers = headers or {}
        self.params = params or {}
        self.method = "GET"
        self._auth_claims: dict | None = None


def _make_mock_handler(return_value: Any = None):
    """Create a simple handler that records whether it was called."""
    calls = []

    def handler(req):
        calls.append(req)
        return return_value or {"status_code": 200, "body": "ok"}

    handler.calls = calls  # type: ignore[attr-defined]
    return handler


class TestRequireAuthDecorator:

    def _valid_token(self, rsa_keys, tenant_id, client_id) -> str:
        priv, _, _ = rsa_keys
        return _make_token(priv, tenant_id, client_id)

    def test_missing_auth_header_returns_401(self, rsa_keys, tenant_id, client_id):
        """AC #1: No Authorization header → 401."""
        from functions.shared.api.auth import require_auth, reset_validator

        handler = _make_mock_handler()
        decorated = require_auth(handler)
        req = MockRequest(headers={})

        resp = decorated(req)
        assert resp.status_code == 401
        assert len(handler.calls) == 0

    def test_non_bearer_scheme_returns_401(self, rsa_keys, tenant_id, client_id):
        """AC #1: Basic scheme → 401."""
        from functions.shared.api.auth import require_auth

        handler = _make_mock_handler()
        decorated = require_auth(handler)
        req = MockRequest(headers={"Authorization": "Basic dXNlcjpwYXNz"})

        resp = decorated(req)
        assert resp.status_code == 401

    def test_valid_token_calls_handler(self, rsa_keys, tenant_id, client_id):
        """AC #2: Valid token → handler is called."""
        from functions.shared.api.auth import require_auth, reset_validator

        priv, _, jwks = rsa_keys
        token = self._valid_token(rsa_keys, tenant_id, client_id)

        handler = _make_mock_handler()
        decorated = require_auth(handler)
        req = MockRequest(headers={"Authorization": f"Bearer {token}"})

        with patch("functions.shared.api.auth.get_validator") as mock_get:
            mock_validator = mock_get.return_value
            mock_validator.validate.return_value = {
                "sub": "u", "oid": "o", "roles": ["DataReader"]
            }
            resp = decorated(req)

        assert len(handler.calls) == 1
        mock_validator.validate.assert_called_once_with(token)

    def test_valid_token_attaches_claims(self, rsa_keys, tenant_id, client_id):
        """AC #2: Claims attached to request._auth_claims."""
        from functions.shared.api.auth import require_auth

        token = self._valid_token(rsa_keys, tenant_id, client_id)
        req = MockRequest(headers={"Authorization": f"Bearer {token}"})

        captured_req = []

        def handler(r):
            captured_req.append(r)
            return {"status_code": 200}

        with patch("functions.shared.api.auth.get_validator") as mock_get:
            mock_get.return_value.validate.return_value = {"sub": "u", "roles": []}
            require_auth(handler)(req)

        assert captured_req[0]._auth_claims == {"sub": "u", "roles": []}

    def test_expired_token_returns_401(self, rsa_keys, tenant_id, client_id):
        """AC #3: Expired token → 401 with 'expired' message."""
        from functions.shared.api.auth import require_auth, AuthError

        priv, _, jwks = rsa_keys
        token = _make_token(priv, tenant_id, client_id, exp_offset=-1)

        handler = _make_mock_handler()
        req = MockRequest(headers={"Authorization": f"Bearer {token}"})

        with patch("functions.shared.api.auth.get_validator") as mock_get:
            mock_get.return_value.validate.side_effect = AuthError("Token has expired")
            resp = require_auth(handler)(req)

        assert resp.status_code == 401
        body = json.loads(resp.get_body())
        assert "expired" in body["message"].lower()
        assert len(handler.calls) == 0

    def test_invalid_signature_returns_401(self, rsa_keys, tenant_id, client_id):
        """AC #3: Tampered token → 401."""
        from functions.shared.api.auth import require_auth, AuthError

        handler = _make_mock_handler()
        req = MockRequest(headers={"Authorization": "Bearer tampered.token.here"})

        with patch("functions.shared.api.auth.get_validator") as mock_get:
            mock_get.return_value.validate.side_effect = AuthError("Invalid token signature")
            resp = require_auth(handler)(req)

        assert resp.status_code == 401

    def test_401_response_has_request_id(self, rsa_keys, tenant_id, client_id):
        """AC (4.3): request_id always in 401 response."""
        from functions.shared.api.auth import require_auth

        req = MockRequest(headers={})
        resp = require_auth(_make_mock_handler())(req)

        body = json.loads(resp.get_body())
        assert "request_id" in body
        assert uuid.UUID(body["request_id"])  # valid UUID

    def test_401_response_has_www_authenticate_header(self):
        """Standard WWW-Authenticate header on 401."""
        from functions.shared.api.auth import require_auth

        req = MockRequest(headers={})
        resp = require_auth(_make_mock_handler())(req)

        assert "WWW-Authenticate" in resp.headers
        assert "Bearer" in resp.headers["WWW-Authenticate"]

    def test_misconfigured_env_returns_401(self):
        """Missing AZURE_AD_* env vars → 401 (not 500)."""
        from functions.shared.api.auth import require_auth, reset_validator
        reset_validator()

        handler = _make_mock_handler()
        req = MockRequest(headers={"Authorization": "Bearer sometoken"})

        env_backup = {k: os.environ.pop(k, None) for k in ("AZURE_AD_TENANT_ID", "AZURE_AD_CLIENT_ID")}
        try:
            resp = require_auth(handler)(req)
            assert resp.status_code == 401
        finally:
            for k, v in env_backup.items():
                if v is not None:
                    os.environ[k] = v
            reset_validator()


# ─── Task 4.3: Integration — full auth flow ───────────────────────────────────

class TestAuthIntegration:
    """Full flow: valid token → validator → handler called / 401 returned."""

    def test_full_flow_valid_token(self, rsa_keys, tenant_id, client_id):
        """AC #2: Valid token flows all the way through."""
        from functions.shared.api.auth import require_auth, JWTValidator

        priv, _, jwks = rsa_keys
        token = _make_token(priv, tenant_id, client_id)

        # Create validator with correct tenant/client and injected JWKS (no HTTP call)
        validator = JWTValidator(tenant_id=tenant_id, client_id=client_id, jwks_override=jwks)

        handler_called = []

        def handler(req):
            handler_called.append(req._auth_claims)
            return {"status_code": 200}

        with patch("functions.shared.api.auth.get_validator", return_value=validator):
            req = MockRequest(headers={"Authorization": f"Bearer {token}"})
            resp = require_auth(handler)(req)

        assert resp == {"status_code": 200}
        assert len(handler_called) == 1
        claims = handler_called[0]
        assert claims["sub"] == "user-sub-001"
        assert claims["tid"] == tenant_id

    def test_full_flow_expired_token_returns_401(self, rsa_keys, tenant_id, client_id):
        """AC #3: Expired token — real validator → 401."""
        from functions.shared.api.auth import require_auth, JWTValidator

        priv, _, jwks = rsa_keys
        token = _make_token(priv, tenant_id, client_id, exp_offset=-10)

        validator = JWTValidator(tenant_id=tenant_id, client_id=client_id, jwks_override=jwks)

        with patch("functions.shared.api.auth.get_validator", return_value=validator):
            req = MockRequest(headers={"Authorization": f"Bearer {token}"})
            resp = require_auth(_make_mock_handler())(req)

        assert resp.status_code == 401
        body = json.loads(resp.get_body())
        assert "expired" in body["message"].lower()

    def test_full_flow_tampered_token_returns_401(self, rsa_keys, tenant_id, client_id):
        """AC #3: Token signed with unknown key → 401."""
        from functions.shared.api.auth import require_auth, JWTValidator
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        _, _, jwks = rsa_keys
        other_key = rsa.generate_private_key(65537, 2048, default_backend())
        token = _make_token(other_key, tenant_id, client_id)

        validator = JWTValidator(tenant_id=tenant_id, client_id=client_id, jwks_override=jwks)

        with patch("functions.shared.api.auth.get_validator", return_value=validator):
            req = MockRequest(headers={"Authorization": f"Bearer {token}"})
            resp = require_auth(_make_mock_handler())(req)

        assert resp.status_code == 401


# ─── Task 3 — Routes public/protected ────────────────────────────────────────

class TestRoutesAuth:
    def test_public_routes_defined(self):
        from functions.shared.api.routes import PUBLIC_ROUTES, ROUTE_HEALTH
        assert ROUTE_HEALTH in PUBLIC_ROUTES

    def test_protected_routes_not_public(self):
        from functions.shared.api.routes import PUBLIC_ROUTES, ROUTE_PRODUCTION, ROUTE_EXPORT
        assert ROUTE_PRODUCTION not in PUBLIC_ROUTES
        assert ROUTE_EXPORT not in PUBLIC_ROUTES
