USER_PERMISSIONS = {
    "29:1HaNlvklep8xVnbSgw9T1RAvnIE5GfMZk_XCrfxipMen96jCAy8nr0QZZMKa1qEZxZK4fP5Ml-ESExPPLqg4dbA": [
        "JD_WORKFLOW",
        "JD_CREATE",
        "JD_FETCH",
        "UNKOWN_INTENT"
    ]
}


def get_permissions(user_id: str):

    return USER_PERMISSIONS.get(user_id, [])
