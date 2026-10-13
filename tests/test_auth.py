from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from framework.auth import AuthManager


def test_concurrent_token_requests_share_one_refresh():
    auth = AuthManager()

    # Count calls to the actual token-generation method.
    with patch.object(
        auth,
        "_request_new_token",
        wraps=auth._request_new_token,
    ) as generate_token:

        with ThreadPoolExecutor(max_workers=10) as executor:
            tokens = list(
                executor.map(
                    lambda _: auth.get_token(),
                    range(10),
                )
            )

    assert all(tokens)
    assert len(set(tokens)) == 1
    assert generate_token.call_count == 1