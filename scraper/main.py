import utils
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Patch Notes API!"}

#########################
# Champions Endpoints
#########################

@app.get("/champions/{patch_version}")
def get_champions_by_version(patch_version: str):
    """
    Endpoint to get champions for a specific patch version.
    """
    return utils.parse_champions(patch_version)

@app.get("/champions/")
def get_latest_champions():
  """
  Endpoint to get champions for the latest patch version.
  """
  patch_version = utils.find_patch_version()
  champions_data = utils.parse_champions(patch_version)
  return champions_data

#########################
# Items Endpoints
#########################

@app.get("/items/{patch_version}")
def get_items_by_version(patch_version: str):
    """
    Endpoint to get items for a specific patch version.
    """
    return utils.parse_items(patch_version)

@app.get("/items/")
def get_latest_items():
    """
    Endpoint to get items for the latest patch version.
    """
    patch_version = utils.find_patch_version()
    items_data = utils.parse_items(patch_version)
    return items_data
