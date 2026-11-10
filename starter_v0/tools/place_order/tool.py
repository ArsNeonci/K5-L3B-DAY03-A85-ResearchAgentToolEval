from commerce_demo.backend import executeTool


def placeOrder(preview_id: str = "", request_id: str = "", confirmation_key: str = "", **extra) -> dict:
    return executeTool("place_order", preview_id=preview_id, request_id=request_id, confirmation_key=confirmation_key, extra=extra)
