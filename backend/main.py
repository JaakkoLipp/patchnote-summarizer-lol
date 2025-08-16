from . import utils
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


@app.get("/other/")
def get_latest_other():
    """
    Endpoint to get other data for the latest patch version.
    """
    return utils.parse_other(utils.find_patch_version())

@app.get("/other/{patch_version}")
def get_other_by_version(patch_version: str):
    """
    Endpoint to get other data for a specific patch version.
    """
    return utils.parse_other(patch_version)


#########################
# Arena Endpoints
#########################


@app.get("/arena/{patch_version}")
def get_arena_by_version(patch_version: str):
    """
    Endpoint to get Arena changes for a specific patch version.
    """
    arena = utils.parse_arena(patch_version) or {"arena": {}}
    mentions = utils.collect_arena_everywhere(patch_version) or {"arena_mentions": []}
    # merge
    arena.update({"mentions": mentions.get('arena_mentions', [])})
    return arena


#########################
# Tagline Endpoints
#########################


@app.get("/tagline/{patch_version}")
def get_tagline_by_version(patch_version: str):
    """
    Endpoint to get the short developer tagline for a specific patch version.
    """
    return utils.parse_tagline(patch_version)


@app.get("/tagline/")
def get_latest_tagline():
    """
    Endpoint to get the short developer tagline for the latest patch version.
    """
    pv = utils.find_patch_version()
    return utils.parse_tagline(pv)


#########################
# Version Endpoint
#########################


@app.get("/version/")
def get_latest_version():
    """
    Endpoint to get the latest patch version as a string (e.g., "25-16").
    """
    v = utils.find_patch_version()
    return {"version": v}


@app.get("/versions/")
def get_recent_versions():
    """
    Endpoint to get the last few patch versions as a list.
    """
    return utils.list_patch_versions(limit=3)


#########################
# One-liner AI Summary Endpoint
#########################


@app.get("/summary/")
def get_latest_summary():
    pv = utils.find_patch_version()
    return utils.generate_one_liner_summary(pv)


@app.get("/summary/{patch_version}")
def get_summary_by_version(patch_version: str):
    return utils.generate_one_liner_summary(patch_version)

@app.get("/arena/")
def get_latest_arena():
    """
    Endpoint to get Arena changes for the latest patch version.
    """
    patch_version = utils.find_patch_version()
    arena = utils.parse_arena(patch_version) or {"arena": {}}
    mentions = utils.collect_arena_everywhere(patch_version) or {"arena_mentions": []}
    arena.update({"mentions": mentions.get('arena_mentions', [])})
    return arena


#########################
# Highlights Endpoints
#########################


@app.get("/highlights/")
def get_latest_highlights():
    pv = utils.find_patch_version()
    return utils.parse_highlights(pv)


@app.get("/highlights/{patch_version}")
def get_highlights_by_version(patch_version: str):
    return utils.parse_highlights(patch_version)


#########################
# Bundle Endpoints
#########################


@app.get("/bundle/")
def get_latest_bundle():
    """Aggregate champions, items, other, arena (+mentions), tagline, highlights for the latest version."""
    pv = utils.find_patch_version()
    return utils.get_bundle(pv) if pv else {}


@app.get("/bundle/{patch_version}")
def get_bundle_by_version(patch_version: str):
    """Aggregate all data for a specific patch version."""
    return utils.get_bundle(patch_version)


@app.on_event("startup")
def prewarm_bundle_cache():
    """Pre-warm the in-memory bundle cache for the latest patch version on startup."""
    try:
        pv = utils.find_patch_version()
        if pv:
            utils.get_bundle(pv)
    except Exception:
        # Non-fatal if prewarm fails
        pass

