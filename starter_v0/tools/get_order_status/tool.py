from commerce_demo.backend import executeTool


def getOrderStatus(order_id: str = "", **extra) -> dict:
    return executeTool("get_order_status", order_id=order_id, extra=extra)
