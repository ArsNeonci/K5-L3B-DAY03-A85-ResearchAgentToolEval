"""Explicit SQLite fixtures and no-send policy for model evals."""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3

from commerce_demo import demoSession, initializeDemoDatabase, issueConfirmation
from tools import TOOL_FUNCTIONS
from tools.preview_order.tool import previewOrder
from tools.place_order.tool import placeOrder


@contextmanager
def evaluation_runtime(*, allow_actions=False):
    root=Path(__file__).resolve().parent/'runtime'
    root.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='eval-',dir=root) as directory:
        database=Path(directory)/'demo.sqlite3'
        initializeDemoDatabase(database)
        with demoSession(database):
            quote=previewOrder('DEMO-NOTEBOOK',2)
            with sqlite3.connect(database) as db:
                db.execute('UPDATE previews SET preview_id=? WHERE preview_id=?',('PREVIEW-EVAL-001',quote['preview_id']))
            db.close()
            quote=previewOrder('DEMO-PEN',1)
            pending=placeOrder(quote['preview_id'],'fixture-order')['pending_action']
            key=issueConfirmation('place_order',pending['payload'])
            order=placeOrder(quote['preview_id'],'fixture-order',key)
            with sqlite3.connect(database) as db:
                db.execute('UPDATE orders SET order_id=? WHERE order_id=?',('DEMO-EVAL-ORDER',order['order']['order_id']))
            db.close()
            original=TOOL_FUNCTIONS['send']
            if not allow_actions:
                def no_send(text='',confirmed=False):
                    if confirmed is not True:
                        return {'status':'needs_confirmation','awaiting_user':True,'question':'Xác nhận nội dung gửi?'}
                    return {'status':'blocked','error':'action_disabled_in_eval','message':'Routing measured; Telegram delivery disabled during eval.'}
                TOOL_FUNCTIONS['send']=no_send
            try:
                yield {'commerce_account':'demo-user-01','preview_id':'PREVIEW-EVAL-001',
                       'order_id':'DEMO-EVAL-ORDER','external_actions_enabled':allow_actions}
            finally:
                TOOL_FUNCTIONS['send']=original
