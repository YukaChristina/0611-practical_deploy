from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
#from db_control import crud, mymodels -----> Azureとの接続のためコメントアウト
from db_control import crud, mymodels_MySQL as mymodels

#UUIDを生成するためのライブラリをインポート
import uuid

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str


app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #"*"から修正済
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.post("/customers")
def create_customer(customer: Customer):

    # 最大試行回数を設定
    MAX_ATTEMPTS = 3
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        #試行回数をインクリメント
        attempts += 1

        # UUIDを生成
        generated_id = str(uuid.uuid4())
        print(f"Attempt{attempts}: generated_id: {generated_id}")


        #IDが存在しない場合のみ処理を実行
        if generated_id != crud.myselect(mymodels.Customers, generated_id):#crud.pyの処理をインポートしている
            #受け取ったデータにcustomer_idを追加
            values = customer.model_dump() #ここで辞書型にする
            values["customer_id"] = generated_id
            print("values:", values)

            #データベースに保存
            tmp = crud.myinsert(mymodels.Customers, values)
            result = crud.myselect(mymodels.Customers, generated_id) #ここではJSON形式

            if result:
                result_obj = json.loads(result) #ここで辞書型（dict）に変換
                return result_obj if result_obj else None
            return None


@app.get("/customers")
def read_one_customer(customer_id: str = Query(...)):
    result = crud.myselect(mymodels.Customers, customer_id)
    print(result)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels.Customers)
    # 結果がNoneの場合は空配列を返す
    if not result:
        return []
    # JSON文字列をPythonオブジェクトに変換
    return json.loads(result)


@app.put("/customers")
def update_customer(customer: Customer):
    values = customer.dict()
    if not values.get("customer_id") or values["customer_id"].strip() == "":
        print("IDを入力してください")
        return {"error":"IDを入力してください"}
    
    values_original = values.copy()
    tmp = crud.myupdate(mymodels.Customers, values)
    result = crud.myselect(mymodels.Customers, values_original.get("customer_id"))
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.delete("/customers")
def delete_customer(customer_id: str = Query(...)):
    result = crud.mydelete(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": customer_id, "status": "deleted"}


@app.get("/fetchtest")
def fetchtest():
    response = requests.get('https://jsonplaceholder.typicode.com/users')
    return response.json()
