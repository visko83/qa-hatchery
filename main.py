from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


@app.get("/registration")
async def register():
    print("/registration endpoint was called")
    return {"message": "Registration successful"}


class Name(BaseModel):
    given: str
    family: str

    def __str__(self):
        return f"{self.given} {self.family}"


class Account(BaseModel):
    name: Name
    id: int | None = None
    child: bool | None = None

    def __str__(self):
        return f"{self.name} ({id}"


account_store = []


@app.post("/registration")
async def register(account: Account):
    account.id = len(account_store)
    account_store.append(account)
    print("/registration registered a new account {account}")
    return {"message": "Registration successful", "id": account.id}


@app.get("/user/{user_id}")
async def user(user_id: int):
    if user_id < len(account_store):
        return account_store[user_id]
    else:
        raise HTTPException(status_code=404, detail=f"User having ID = {user_id} cannot be found")
