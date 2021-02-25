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
