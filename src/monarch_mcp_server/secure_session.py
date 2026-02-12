"""
Secure session management for Monarch Money MCP Server using keyring.
"""

import keyring
import logging
import os
from typing import Optional
from monarchmoney import MonarchMoney, MonarchMoneyEndpoints, LoginFailedException
from gql.transport.exceptions import TransportServerError

logger = logging.getLogger(__name__)

# Keyring service identifiers
KEYRING_SERVICE = "com.mcp.monarch-mcp-server"
KEYRING_USERNAME = "monarch-token"


class SecureMonarchSession:
    """Manages Monarch Money sessions securely using the system keyring."""

    def save_token(self, token: str) -> None:
        """Save the authentication token to the system keyring."""
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, token)
            logger.info("✅ Token saved securely to keyring")

            # Clean up any old insecure files
            self._cleanup_old_session_files()

        except Exception as e:
            logger.error(f"❌ Failed to save token to keyring: {e}")
            raise

    def load_token(self) -> Optional[str]:
        """Load the authentication token from the system keyring."""
        try:
            token = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if token:
                logger.info("✅ Token loaded from keyring")
                return token
            else:
                logger.info("🔍 No token found in keyring")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to load token from keyring: {e}")
            return None

    def delete_token(self) -> None:
        """Delete the authentication token from the system keyring."""
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            logger.info("🗑️ Token deleted from keyring")

            # Also clean up any old insecure files
            self._cleanup_old_session_files()

        except keyring.errors.PasswordDeleteError:
            logger.info("🔍 No token found in keyring to delete")
        except Exception as e:
            logger.error(f"❌ Failed to delete token from keyring: {e}")

    def get_authenticated_client(self) -> Optional[MonarchMoney]:
        """Get an authenticated MonarchMoney client."""
        token = self.load_token()
        if not token:
            return None

        try:
            client = MonarchMoney(token=token)
            logger.info("✅ MonarchMoney client created with stored token")
            return client
        except Exception as e:
            logger.error(f"❌ Failed to create MonarchMoney client: {e}")
            return None

    def save_authenticated_session(self, mm: MonarchMoney) -> None:
        """Save the session from an authenticated MonarchMoney instance."""
        if mm.token:
            self.save_token(mm.token)
        else:
            logger.warning("⚠️  MonarchMoney instance has no token to save")

    def _cleanup_old_session_files(self) -> None:
        """Clean up old insecure session files."""
        cleanup_paths = [
            ".mm/mm_session.pickle",
            "monarch_session.json",
            ".mm",  # Remove the entire directory if empty
        ]

        for path in cleanup_paths:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        os.remove(path)
                        logger.info(f"🗑️ Cleaned up old insecure session file: {path}")
                    elif os.path.isdir(path) and not os.listdir(path):
                        os.rmdir(path)
                        logger.info(f"🗑️ Cleaned up empty session directory: {path}")
            except Exception as e:
                logger.warning(f"⚠️  Could not clean up {path}: {e}")


def is_auth_error(exc: Exception) -> bool:
    """Return True if the exception signals an expired or invalid auth token.

    Covers the two concrete error paths from the monarchmoney / gql stack:

    1. Expired token on a GraphQL call -> gql raises
       ``TransportServerError`` with ``.code == 401`` or ``.code == 403``.
    2. Token/headers never set -> monarchmoney raises
       ``LoginFailedException``.

    For 403 responses, we distinguish genuine auth failures from WAF
    (Web Application Firewall) blocks.  Monarch's WAF returns 403 with
    an HTML body when it rejects input containing patterns like
    ``<script>`` tags.  These are NOT auth errors and must not trigger
    token deletion / re-auth.

    gql wraps the underlying ``aiohttp.ClientResponseError`` as the
    ``__cause__`` of the ``TransportServerError``.  The cause carries
    the original response headers, letting us check ``Content-Type``:
    API auth errors return ``application/json``; WAF blocks return
    ``text/html``.
    """
    if isinstance(exc, TransportServerError):
        code = getattr(exc, "code", None)
        if code == 401:
            return True
        if code == 403:
            cause = exc.__cause__
            if cause is not None:
                headers = getattr(cause, "headers", None) or {}
                content_type = str(headers.get("content-type", "")).lower()
                if "application/json" not in content_type:
                    logger.warning(
                        "403 with content-type %r — likely WAF block, not auth error",
                        content_type,
                    )
                    return False
            return True
    if isinstance(exc, LoginFailedException):
        return True
    return False


# Global session manager instance
secure_session = SecureMonarchSession()
