from fastapi import FastAPI
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


def get_id():
    latest = 0
    while True:
        yield latest
        latest += 1


get_id = get_id()


@app.post("/registration")
async def register(account: Account):
    account.id = next(get_id)
    print("/registration registered a new account {account}")
    return {"message": "Registration successful", "id": account.id}
