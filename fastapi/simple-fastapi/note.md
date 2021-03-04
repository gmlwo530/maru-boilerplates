```python
@app.get("/")
async def root():
    ...
```

In our case, this decorator tells FastAPI that the function below corresponds to the path / with an operation get.

It is the "path operation decorator".

---

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

```text
{"item_id":3}
```

Notice that the value your function received (and returned) is 3, as a Python int, not a string "3".

So, with that type declaration, FastAPI gives you automatic request "parsing".

"parsing": converting the string that comes from an HTTP request into Python data

여기서 만약 정수가 아닌 item_id를 호출하면 `http://127.0.0.1:8000/items/4.2`

에러가 반환 된다

```json
{
  "detail": [
    {
      "loc": ["path", "item_id"], // 어디서 잘 못 됐는지까지 알려준다!
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

```python
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

```

Because path operations are evaluated in order, you need to make sure that the path for /users/me is declared before the one for /users/{user_id}

---

But you need file_path itself to contain a path, like home/johndoe/myfile.txt.

So, the URL for that file would be something like: /files/home/johndoe/myfile.txt.

But OpenAPI did not support this.

```python
# /files/{file_path:path} <- starlette option
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

---

- If the parameter is also declared in the path, it will be used as a path parameter.
- If the parameter is of a singular type (like int, float, str, bool, etc) it will be interpreted as a query parameter.
- If the parameter is declared to be of the type of a Pydantic model, it will be interpreted as a request body.

---

```python
@app.get("/items/")
async def read_items(q: Optional[str] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

_FastAPI will know that the value of q is not required because of the default value = None. The `Optional` in `Optional[str]` is not used by FastAPI, but will allow your editor to give you better support and detect errors._

_Having a default value also makes the parameter optional._

---

@app.get("/items/")
async def read_items(q: Optional[List[str]] = Query(None)):
return {"q": q}

**To declare a query parameter with a type of list, like in the example above, you need to explicitly use `Query`, otherwise it would be interpreted as a request body.**

---

```python
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(..., title="The ID of the item to get"),
    q: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

A path parameter is always required as it has to be part of the path.

So, you should declare it with ... to mark it as required.

Nevertheless, even if you declared it with None or set a default value, it would not affect anything, it would still be always required.

---

```python
@app.get("/items/{item_id}")
async def read_items(
    *, item_id: int = Path(..., title="The ID of the item to get"), q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results
```

If you want to declare the q query parameter without a Query nor any default value, and the path parameter item_id using Path, and have them in a different order, Python has a little special syntax for that.

Pass \*, as the first parameter of the function.

Python won't do anything with that \*, but it will know that all the following parameters should be called as keyword arguments (key-value pairs), also known as kwargs.

---

When you import Query, Path and others from fastapi, they are actually functions.

That when called, return instances of classes of the same name.

So, you import Query, which is a function. And when you call it, it returns an instance of a class also named Query.

These functions are there (instead of just using the classes directly) so that your editor doesn't mark errors about their types.

That way you can use your normal editor and coding tools without having to add custom configurations to disregard those errors.

---

Have in mind that JSON only supports str as keys.

But Pydantic has automatic data conversion.

This means that, even though your API clients can only send strings as keys, as long as those strings contain pure integers, Pydantic will convert them and validate them.

And the dict you receive as weights will actually have int keys and float values.

---

```python
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: List[str] = []


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item
```

FastAPI will use this response_model to:

- Convert the output data to its type declaration.
- Validate the data.
- Add a JSON Schema for the response, in the OpenAPI path operation.
- Will be used by the automatic documentation systems.
  But most importantly:

- Will limit the output data to that of the model. We'll see how that's important below.
  Technical Details

_The response model is declared in this parameter instead of as a function return type annotation, because the path function may not actually return that response model but rather return a dict, database object or some other model, and then use the response_model to perform the field limiting and serialization._

만약 반환 값을 다음과 같이 조작해도, `q` 필드는 반환 되지 않는다. 왜냐하면 response_model 선언으로 인해 `@app.post`에서 field를 제한 해주기 때문이다.

```python
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.dict()

    item_dict.update({"q": "Hello"})
    return item_dict
```

---

```python
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}


@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]
```

But it is still recommended to use the ideas above, using multiple classes, instead of these parameters(`response_model_include`or `response_model_exclude`).

This is because the JSON Schema generated in your app's OpenAPI (and the docs) will still be the one for the complete model, even if you use response_model_include or response_model_exclude to omit some attributes.

This also applies to response_model_by_alias that works similarly.

---

[Unwrapping a dict](https://fastapi.tiangolo.com/tutorial/extra-models/#unwrapping-a-dict)

---

`File`와 `UploadFile`

If you declare the type of your path operation function parameter as bytes, FastAPI will read the file for you and you will receive the contents as bytes.

Have in mind that this means that the whole contents will be stored in memory. This will work well for small files.

But there are several cases in which you might benefit from using UploadFile.

---

Using [UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile) has several advantages over bytes:

- It uses a "spooled" file:
  - A file stored in memory up to a maximum size limit, and after passing this limit it will be stored in disk.
- This means that it will work well for large files like images videos, large binaries, etc. without consuming all the memory.
- You can get metadata from the uploaded file.
- It has a file-like async interface.
- It exposes an actual Python SpooledTemporaryFile object that you can pass directly to other libraries that expect a file-like object.

---

When raising an HTTPException, you can pass any value that can be converted to JSON as the parameter detail, not only str.

You could pass a dict, a list, etc.

They are handled automatically by FastAPI and converted to JSON.

---

- `PUT`: Update
- `PATCH`: Partial updates
