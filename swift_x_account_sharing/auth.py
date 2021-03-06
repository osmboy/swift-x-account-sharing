"""Authentication module for the swift-sharing-request."""

# The authentication is done via requests signed with a pre-whitelisted token.
# This is done to prevent invalid usage. New tokens can be created either
# manually on the platform that's running the software, or by
# pre-authenticating via Openstack Keystone.

# Authentication engine is written as an aiohttp middleware function.


import os
import typing
import hmac

import aiohttp.web


AiohttpHandler = typing.Callable[[aiohttp.web.Request], aiohttp.web.Response]


async def read_in_keys(
        app: aiohttp.web.Application
):
    """Read in keys to the application."""
    keys = os.environ.get("SWIFT_UI_API_AUTH_TOKENS", None)
    app["tokens"] = keys.split(",") if keys is not None else []
    if app["tokens"]:
        app["tokens"] = [
            token.encode("utf-8") for token in app["tokens"]
        ]


async def test_signature(
        tokens: typing.List[bytes],
        signature: str,
        message: str,
) -> bool:
    """Validate signature against the given tokens."""
    byte_message = message.encode("utf-8")
    for token in tokens:
        digest = hmac.new(
            token,
            byte_message,
            digestmod="sha256"
        ).hexdigest()
        if digest == signature:
            return
    raise aiohttp.web.HTTPUnauthorized(
        reason="Missing valid query signature"
    )


@aiohttp.web.middleware
async def handle_validate_authentication(
        request: aiohttp.web.Request,
        handler: AiohttpHandler,
) -> aiohttp.web.Response:
    """Handle the authentication of a response as a middleware function."""
    try:
        signature = request.query["signature"]
        validity = request.query["valid"]
        path = request.url.path
    except KeyError:
        raise aiohttp.web.HTTPClientError(
            reason="Query string missing validity or signature."
        )

    await test_signature(
        request.app["tokens"],
        signature,
        validity + path
    )

    return await handler(request)
