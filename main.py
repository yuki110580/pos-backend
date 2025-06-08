# backend/main.py

from fastapi import FastAPI
from db import get_connection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切なドメインに制限してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/items/{code}")
def get_item(code: str):
    conn = get_connection()
    if conn is None:
        return {"error": "DB接続に失敗しました"}

    cursor = conn.cursor(dictionary=True)
    query = "SELECT PRD_ID, CODE, NAME, PRICE FROM items WHERE CODE = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return result
    else:
        return None


from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# POSTリクエストのボディ形式を定義
class PurchaseItem(BaseModel):
    PRD_ID: int
    PRD_CODE: str
    PRD_NAME: str
    PRD_PRICE: int

class PurchaseRequest(BaseModel):
    EMP_CD: Optional[str] = "9999999999"
    STORE_CD: Optional[str] = "30"
    POS_NO: Optional[str] = "90"
    items: List[PurchaseItem]


@app.post("/purchase")
def make_purchase(purchase: PurchaseRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 取引テーブルに登録
    insert_transaction = """
        INSERT INTO transactions (EMP_CD, STORE_CD, POS_NO, TOTAL_AMT)
        VALUES (%s, %s, %s, %s)
    """
    emp_cd = purchase.EMP_CD if purchase.EMP_CD else "9999999999"
    store_cd = purchase.STORE_CD if purchase.STORE_CD else "30"
    pos_no = purchase.POS_NO if purchase.POS_NO else "90"
    cursor.execute(insert_transaction, (emp_cd, store_cd, pos_no, 0))
    conn.commit()

    # 2. 登録された取引IDを取得
    transaction_id = cursor.lastrowid

    # 3. 明細登録と合計金額計算
    total_amount = 0
    for i, item in enumerate(purchase.items, start=1):
        insert_detail = """
            INSERT INTO transaction_items (
                TRD_ID, DTL_ID, PRD_ID, PRD_CODE, PRD_NAME, PRD_PRICE
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_detail, (
            transaction_id, i, item.PRD_ID, item.PRD_CODE, item.PRD_NAME, item.PRD_PRICE
        ))
        total_amount += item.PRD_PRICE

    # 4. 合計金額を更新
    update_total = """
        UPDATE transactions
        SET TOTAL_AMT = %s
        WHERE TRD_ID = %s
    """
    cursor.execute(update_total, (total_amount, transaction_id))
    conn.commit()

    # 後片付け
    cursor.close()
    conn.close()

    return {"success": True, "transaction_id": transaction_id, "total_amount": total_amount}
