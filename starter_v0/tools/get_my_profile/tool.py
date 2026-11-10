from commerce_demo.backend import executeTool


def getMyProfile(**extra) -> dict:
    return executeTool("get_my_profile", extra=extra)
