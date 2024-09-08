from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI

from lib.tlite import TLite

tLite = TLite()
app = FastAPI()


class Item(BaseModel):
    query: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/assist", status_code=200)
def assist_assist_post(res: Item):
    try:
        return tLite.send_promt(res.query)
    except ValueError:
        print("Oops!  That was no valid number.  Try again...")
