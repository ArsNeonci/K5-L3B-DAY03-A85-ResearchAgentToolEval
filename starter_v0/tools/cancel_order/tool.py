from commerce_demo.backend import executeTool


def cancelOrder(order_id: str = "", confirmation_key: str = "", **extra) -> dict:
    return executeTool("cancel_order", order_id=order_id, confirmation_key=confirmation_key, extra=extra)
