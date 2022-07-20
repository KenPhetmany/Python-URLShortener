import validators
from fastapi import FastAPI, HTTPException
from . import schemas

app = FastAPI()

# path operationm decorator to associate the root path with this function.
# FastAPI listens to the root path and delegates all incoming GET requests.


@app.get("/")
def read_root():
    return "Welcome to the URL shortener API :)"


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

# define create_url endpoint which expects a URL string as a POST request body


@app.post("/url")
def create_url(url: schemas.URLBase):
    # check if url.target_url is a valid URL otherwise send bad request
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")
    return f"TODO: Create database entry for: {url.target_url}"
