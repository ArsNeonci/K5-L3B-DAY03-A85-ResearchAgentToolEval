from commerce_demo.backend import executeTool


def previewOrder(product_id: str = "", quantity: int | None = None, shipping_address: str = "", **extra) -> dict:
    return executeTool("preview_order", product_id=product_id, quantity=quantity, shipping_address=shipping_address, extra=extra)
