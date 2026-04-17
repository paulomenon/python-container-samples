"""Product CRUD API."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Products Backend")

_products: dict[int, dict] = {}
_next_id = 1


class ProductCreate(BaseModel):
    name: str
    price: float


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


@app.get("/products")
def list_products():
    return list(_products.values())


@app.post("/products", status_code=201)
def create_product(body: ProductCreate):
    global _next_id
    pid = _next_id
    _next_id += 1
    product = {"id": pid, "name": body.name, "price": body.price}
    _products[pid] = product
    return product


@app.get("/products/{product_id}")
def get_product(product_id: int):
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    return _products[product_id]


@app.put("/products/{product_id}")
def replace_product(product_id: int, body: ProductCreate):
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    _products[product_id] = {"id": product_id, "name": body.name, "price": body.price}
    return _products[product_id]


@app.patch("/products/{product_id}")
def patch_product(product_id: int, body: ProductUpdate):
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    data = _products[product_id]
    if body.name is not None:
        data["name"] = body.name
    if body.price is not None:
        data["price"] = body.price
    return data


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    del _products[product_id]
