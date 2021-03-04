from typing import Optional, List, Union
from enum import Enum
from fastapi import (
    FastAPI,
    Query,
    Path,
    Body,
    Cookie,
    Header,
    Form,
    File,
    UploadFile,
    HTTPException,
)
from pydantic import BaseModel, Field, EmailStr


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/items")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]


# @app.get("/items/")
# async def read_items(
#     q: Optional[str] = Query(None, min_length=3, max_length=50, regex="^fixedquery$")
# ):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# use parameter with required and validation
# @app.get("/items/")
# async def read_items(q: str = Query(..., min_length=3)):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


# query parameter list / multi values
# To declare a query parameter with a type of list, like in the example above, you need to explicitly use Query, otherwise it would be interpreted as a request body.
# @app.get("/items/")
# async def read_items(q: Optional[List[str]] = Query(None)):
#     return {"q": q}


# query parameter list / multi values with default
# @app.get("/items/")
# async def read_items(q: Optional[List[str]] = Query(["foo", "bar"])):
#     return {"q": q}

# alias and deprecated
# @app.get("/items/")
# async def read_items(
#     q: Optional[str] = Query(
#         None,
#         title="Query String",
#         description="Query String description",
#         min_length=3,
#         alias="item-query",
#         deprecated=True,
#     )
# ):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(..., title="The ID of the item to get"),
    q: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# @app.get("/items/{item_id}")
# async def read_item_optional(
#     item_id: int, q: Optional[str] = None, short: bool = False
# ):
#     item = {"item_id": item_id}

#     if q:
#         return {"item_id": item_id, "q": q}

#     if not short:
#         item.update(
#             {"description": "This is an amazing item that has a long description"}
#         )

#     return item


@app.post("/items/", response_model=Item)
async def create_item(
    item: Item = Body(
        ...,
        example={
            "name": "Foo123",
            "description": "A very nice Item!!!!",
            "price": 35333.4,
            "tax": 3333.2,
        },
    ),
    q: Optional[str] = None,
):
    item_dict = item.dict()

    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    result = item_dict

    if q:
        result.update({"q": q})

    return result


@app.put("/items/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: int = Body(..., ge=1)
):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Optional[str] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}

    if q:
        item.update({"q": q})

    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app.get("/cookies/")
async def read_cookies(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}


@app.get("/headers/")
async def read_headers(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}


@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}
