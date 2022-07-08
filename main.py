from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.responses import HTMLResponse

DESTINATIONS = {"Hungary": {"Budapest": ["Four Seasons", "Hilton", "Kempinski", "Corinthia"]},
                "Spain": {"Barcelona": ["Hilton", "InterContinental", "Hyatt Regency", "Hotel Vincci Gala"]},
                "Germany": {"Berlin": ["Park Inn", "Hilton", "Pullman Schweizerhof"]},
                "Ireland": {"Belfast": ["The Merchant", "Europa Hotel", "The Fitzwilliam Hotel"]},
                "France": {"Bordeaux": ["InterContinental", "Hotel Des Quinconces"]}}

app = FastAPI()

security = HTTPBasic()


def check_credentials(credentials: HTTPBasicCredentials):
    found_user = list(filter(lambda a: a.username == credentials.username, account_store))
    if not found_user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Username cannot be found")
    if found_user[0].password != credentials.password:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Bad password")


class Name(BaseModel):
    given: str
    family: str

    def __str__(self):
        return f"{self.given} {self.family}"


class Account(BaseModel):
    name: Name
    username: str
    password: str
    id: int | None = None
    child: bool | None = None

    def __str__(self):
        return f"{self.name} ({id}"

@app.get("/")
async def home():
  return HTMLResponse("<h1>Hello!</h1>")
      
@app.get("/destinations")
async def destinations(credentials: HTTPBasicCredentials = Depends(security)):
    check_credentials(credentials)
    return DESTINATIONS


class Booking(BaseModel):
    id: int
    country: str
    city: str
    hotel: str
    from_date: datetime
    to_date: datetime


class BookingStore:
    def __init__(self):
        self.bookings: Dict[int, Dict[int, Booking]] = {}
        self.next_available_booking_id: int = 0

    def add(self, user_id: int, booking: Booking) -> Booking:
        booking.id = self.next_available_booking_id
        if user_id in self.bookings:
            self.bookings[user_id][self.next_available_booking_id] = booking
        else:
            self.bookings[user_id] = {self.next_available_booking_id: booking}
        self.next_available_booking_id += 1
        return booking

    def list(self, user_id: int) -> Dict[int, Booking]:
        return self.bookings[user_id]

    def get(self, user_id: int, booking_id: int) -> Booking:
        return self.bookings[user_id][booking_id]

    def delete(self, user_id: int, booking_id: int):
        del self.bookings[user_id][booking_id]
        if not self.bookings[user_id]:
            del self.bookings[user_id]


booking_store = BookingStore()


@app.post("/user/{user_id}/bookings")
async def create_booking(user_id: int, booking: Booking, credentials: HTTPBasicCredentials = Depends(security)):
    check_credentials(credentials)
    if booking.country not in DESTINATIONS:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid country")
    if booking.city not in DESTINATIONS[booking.country]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid city")
    if booking.hotel not in DESTINATIONS[booking.country][booking.city]:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid hotel")
    booking = booking_store.add(user_id, booking)
    return JSONResponse(status_code=HTTPStatus.CREATED,
                        content={"message": "Booking confirmed", "details": jsonable_encoder(booking)})


@app.get("/user/{user_id}/bookings")
async def get_all_bookings_of_account(user_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    check_credentials(credentials)
    return booking_store.list(user_id=user_id)


@app.get("/user/{user_id}/bookings/{booking_id}")
async def get_all_bookings_of_account(user_id: int, booking_id: int,
                                      credentials: HTTPBasicCredentials = Depends(security)):
    check_credentials(credentials)
    return booking_store.get(user_id, booking_id)


@app.delete("/user/{user_id}/bookings/{booking_id}")
async def delete_booking_of_account(user_id: int, booking_id: int,
                                    credentials: HTTPBasicCredentials = Depends(security)):
    check_credentials(credentials)
    return booking_store.delete(user_id, booking_id)


account_store: List[Account] = []


@app.post("/registration")
async def register(account: Account):
    account.id = len(account_store)
    account_store.append(account)
    print("/registration registered a new account {account}")
    return {"message": "Registration successful", "id": account.id}


@app.get("/user/{user_id}")
async def user(user_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    check_credentials(credentials)
    if user_id < len(account_store):
        found_user = deepcopy(account_store[user_id])
        found_user.password = None
        return found_user
    else:
        raise HTTPException(status_code=404, detail=f"User having ID = {user_id} cannot be found")
