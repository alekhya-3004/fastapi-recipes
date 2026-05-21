from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from typing import Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session

from database import get_db, engine
from models import Recipe, Base
from schemas import RecipeCreate, Recipe as RecipeSchema

# create all tables in the database if they don't exist
Base.metadata.create_all(bind=engine)

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
def recipes_page(request: Request, db: Session = Depends(get_db)):
    """
    Render the recipes as a web page using the Jinja2 template.
    """
    recipes = db.query(Recipe).all()
    return TEMPLATES.TemplateResponse(request, "index.html", {"recipes": recipes})

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
def fetch_recipe(recipe_id: int, db: Session = Depends(get_db))-> dict:
    """
    Fetch a recipe from a list using its ID from the URL.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

# query parameter
# GET API
# This API searches recipes by a keyword and returns limited results.
@api_router.get("/search/",status_code=200)
def search_recipes(keyword:Optional[str]=None, limit: Optional[int]=10, db: Session = Depends(get_db)) -> list:
    """
    This API searches recipes by a keyword and returns limited results.
    """
    recipes = db.query(Recipe).filter(Recipe.label.ilike(f"%{keyword}%")).limit(limit).all()
    return recipes

# GET API
# search by path parameter as well as query param
# error handling for missing keyword query parameter
@api_router.get("/search/{keyword}", status_code=200)
def search_recipes_by_keyword(keyword: str, limit: Optional[int]=10, db: Session = Depends(get_db)) -> list:
    """
    Search recipes using a path keyword.
    """
    # error handling for missing keyword query parameter
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword query parameter is required")
    recipes = db.query(Recipe).filter(Recipe.label.ilike(f"%{keyword}%")).limit(limit).all()
    return recipes

# DELETE API
# This API deletes a recipe from the database using its ID.
@api_router.delete("/recipe/{recipe_id}", status_code=200)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Delete a recipe from the database using its ID.
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.commit()
    return {"msg": f"Recipe {recipe_id} deleted successfully"}

# POST API
# This API takes recipe data from the user, creates a new recipe, stores it, and returns it.
@api_router.post("/recipe/", status_code=201, response_model=RecipeSchema)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """
    This API takes recipe data from the user, creates a new recipe, stores it, and returns it.
    """
    new_recipe = Recipe(
        label=recipe.label,
        source=recipe.source,
        url=str(recipe.url),
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe

# include the API router in the FastAPI app
app.include_router(api_router)

# Run the application using Uvicorn when this script is executed directly
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="debug")
