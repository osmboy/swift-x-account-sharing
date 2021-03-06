"""Sharing backend API specification and implementation."""


import logging
import asyncio

import aiohttp.web
from asyncpg import InterfaceError


MODULE_LOGGER = logging.getLogger("api")


def handle_dropped_connection(request):
    """Handle dropped database connection."""
    MODULE_LOGGER.log(
        logging.ERROR,
        "Lost database connection, reconnecting..."
    )
    request.app["db_conn"].erase()
    asyncio.ensure_future(
        request.app["db_conn"].open()
    )
    raise aiohttp.web.HTTPServiceUnavailable(
        reason="No database connection."
    )


async def has_access_handler(request):
    """Handle has-access endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        access_list = await request.app["db_conn"].get_access_list(
            request.match_info["user"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following access list: %s", str(access_list)
    )

    return aiohttp.web.json_response(access_list)


async def access_details_handler(request):
    """Handle access-details endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        access_details = \
            await request.app["db_conn"].get_access_container_details(
                request.match_info["user"],
                request.query["owner"],
                request.match_info["container"])
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following access details: %s", str(access_details)
    )

    return aiohttp.web.json_response(access_details)


async def gave_access_handler(request):
    """Handle gave-access endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        shared_list = await request.app["db_conn"].get_shared_list(
            request.match_info["owner"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following shared container listing: %s",
        str(shared_list)
    )

    return aiohttp.web.json_response(shared_list)


async def shared_details_handler(request):
    """Handle shared-details endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        shared_details = \
            await request.app["db_conn"].get_shared_container_details(
                request.match_info["owner"],
                request.match_info["container"])
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Returning following shared container details: %s",
        str(shared_details)
    )

    return aiohttp.web.json_response(shared_details)


async def share_container_handler(request):
    """Handle share-container endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        shared = await request.app["db_conn"].add_share(
            request.match_info["owner"],
            request.match_info["container"],
            request.query["user"].split(","),
            request.query["access"].split(","),
            request.query["address"]
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Added following new shares: %s", str(shared)
    )

    return aiohttp.web.json_response(shared)


async def edit_share_handler(request):
    """Handle container shared rights editions."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        edited = await request.app["db_conn"].edit_share(
            request.match_info["owner"],
            request.match_info["container"],
            request.query["user"].split(","),
            request.query["access"].split(",")
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Edited following shares: %s", str(edited)
    )

    return aiohttp.web.json_response(edited)


async def delete_share_handler(request):
    """Handle unshare-container endpoint query."""
    # Future authorization check here

    # Check for incorrect client query here

    try:
        deleted = await request.app["db_conn"].delete_share(
            request.match_info["owner"],
            request.match_info["container"],
            request.query["user"].split(",")
        )
    except InterfaceError:
        handle_dropped_connection(request)

    MODULE_LOGGER.log(
        logging.DEBUG,
        "Deleted following shares: %s", str(deleted)
    )

    if not deleted:
        raise aiohttp.web.HTTPNotFound()

    return aiohttp.web.Response(
        status=204,
        body="OK"
    )
