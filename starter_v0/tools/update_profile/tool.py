from commerce_demo.backend import executeTool


def updateProfile(field: str = "", new_value: str = "", confirmation_key: str = "", **extra) -> dict:
    return executeTool("update_profile", field=field, new_value=new_value, confirmation_key=confirmation_key, extra=extra)
