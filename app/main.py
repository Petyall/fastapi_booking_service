from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from typing import Optional
from datetime import date

from bookings.router import router as router_bookings
from users.router import router as router_users
from hotels.router import router as router_hotels
from pages.router import router as router_pages
from images.router import router as router_images

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_pages)
app.include_router(router_images)