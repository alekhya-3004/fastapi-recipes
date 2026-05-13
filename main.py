from fastapi import FastAPI, APIRouter, HTTPException, Request

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from typing import Optional, Any
from pathlib import Path

from recipe_data import RECIPES

from schemas import Recipe, RecipeCreate, RecipeSearchResults

# combining path of the currect folder with the templates folder to get the path to the templates
# define base path for templates
BASE_PATH=Path(__file__).resolve().parent
# initialize Jinja2 templates
TEMPLATES=Jinja2Templates(directory=str(BASE_PATH / "templates"))

# initialize FastAPI app
app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

# initialize API router
api_router = APIRouter()

# define endpoint to render recipes as a web page
# This endpoint uses the Jinja2 template to render the recipes as a web page. 
# It takes a Request object as a parameter and returns an HTML response. 
# The recipes are passed to the template as a context variable.
@api_router.get("/recipes", response_class=HTMLResponse)
def recipes_page(request: Request):
    """
    Render the recipes as a web page using the Jinja2 template.
    """
    return TEMPLATES.TemplateResponse(request, "index.html", {"recipes": RECIPES})

# define root endpoint
@api_router.get("/", status_code=200)
# This is a simple root endpoint that returns a welcome message.
def root() -> dict:
    """
    Root GET
    """
    return {"msg": "Hello, World!"}

# path parameter
# GET API
# Fetch a recipe from a list using its ID from the URL.
# basic error handling
# fetch recipe by ID, if not found return 404 error raise httpexception instead of returning dict with error message and status code, use HTTPException from fastapi
@api_router.get("/recipe/{recipe_id}",status_code=200)
def fetch_recipe(recipe_id: int)-> dict:
    """
    Fetch a recipe from a list using its ID from the URL.
    """
    for recipe in RECIPES:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")

# query parameter
# GET API
# This API searches recipes by a keyword and returns limited results.
@api_router.get("/search/",status_code=200)
def search_recipes(keyword:Optional[str]=None,limit: Optional[int]=10) -> list[dict]:
    """
    This API searches recipes by a keyword and returns limited results.
    """
    result=[]
    for recipe in RECIPES:
        if keyword.lower() in recipe["label"].lower():
            result.append(recipe)
    return result[:limit]

# GET API       
# search by path parameter as well as query param
# error handling for missing keyword query parameter
@api_router.get("/search/{keyword}", status_code=200)
def search_recipes_by_keyword(keyword: str, limit: Optional[int]=10) -> list[dict]:
    """
    Search recipes using a path keyword.
    """
    # error handling for missing keyword query parameter
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword query parameter is required")
    result=[]
    for recipe in RECIPES:
        if keyword.lower() in recipe["label"].lower():
            result.append(recipe)
    return result[:limit]

# POST API
# This API takes recipe data from the user, creates a new recipe, stores it, and returns it.
@api_router.post("/recipe/",status_code=201)
def create_recipe(recipe: RecipeCreate) -> dict:
    """
    This API takes recipe data from the user, creates a new recipe, stores it, and returns it.
    """
    new_recipe={
        "id": len(RECIPES)+1,
        "label": recipe.label,
        "source": recipe.source,
        "url": recipe.url,
    }
    RECIPES.append(new_recipe)
    return new_recipe

# include the API router in the FastAPI app
app.include_router(api_router)

# Run the application using Uvicorn when this script is executed directly
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="debug")