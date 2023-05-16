from fastapi import FastAPI, Query
from typing import Optional
from datetime import date

from bookings.router import router as router_bookings
from users.router import router as router_users

app = FastAPI()

app.include_router(router_users)
app.include_router(router_bookings)

@app.get("/hotels")
def get_hotels(
    location: str, 
    date_from: date,
    date_to: date,
    has_spa: Optional[bool] = None,
    stars: Optional[int] = Query(None, ge=1, le=5)
):
    return location, date_from