from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Sequence

# define a Pydantic base model for a recipe
# main model- output model
class Recipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    label:str
    source:str
    url:str

# define a Pydantic model for search results, which contains a sequence of Recipe objects
# this wraps list of recipes
class RecipeSearchResults(BaseModel):
    results: Sequence[Recipe]

# define a Pydantic model for creating a new recipe, which includes the label, source, url, and submitter_id fields
# input model
class RecipeCreate(BaseModel):
    label: str
    source: str
    url: HttpUrl
    submitter_id: int


