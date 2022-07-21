# import the functions and classes from external modules

from os import stat
import secrets

import validators
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
# import the functions and classes from external modules
from . import models, schemas, crud
from .config import get_settings
# import SessionLocal and engine
from .database import SessionLocal, engine
from starlette.datastructures import URL

app = FastAPI()

# binds atbase engine with models.Base.metadata_create_all()
# if database in engine doesn't exist yet, then it will be created with the tables

models.Base.metadata.create_all(bind=engine)
# path operationm decorator to associate the root path with this function.
# FastAPI listens to the root path and delegates all incoming GET requests.


def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist "
    raise HTTPException(status_code=404, detail=message)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

# path operation decorator that makes the create_url() function below responds to any POST
# request at the /url path


@app.post("/url", response_model=schemas.URLInfo)
# defines create_url() which requires a URLBase schema as an argument and depends
# by passing into Depends(), you establish a database session for the request and close when finished
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    # Make sre the provided target_url is a valid URL
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")

    # provide random strings for chars and key
    # create a database entry for your target_url
    db_url = crud.create_db_url(db=db, url=url)
    db_url.url = db_url.key
    db_url.admin_url = db_url.secret_key
    return get_admin_info(db_url)


@app.get("/{url_key}")
# allow GET requests for the URL that you provide as an argument
# with the "/{url_key}" argument, the function will be called anytime a client
# requests a URL that matches the host and key pattern
def forward_to_target_url(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # look for an active URL entry with the provided url_key in your database
    # if a database is entry is found than you return the RedirectResponse with target_url
    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@app.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=schemas.URLInfo,
)
def get_url_info(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url


@app.delete("/admin/{secret_key}")
def delete_url(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)
