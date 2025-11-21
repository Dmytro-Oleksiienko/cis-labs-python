import requests
import json

BASE = "http://localhost:8000/api/products"


def main():
    print("== GET /api/products ==")
    resp = requests.get(BASE)
    print(resp.status_code, resp.text)

    print("\n== POST /api/products ==")
    body = {
        "name": "Console Item",
        "manufacturer": "LG",
        "country": "Korea",
        "color": "Black",
        "price": 1234.0
    }
    post = requests.post(BASE, json=body)
    print(post.status_code, post.text)

    try:
        new_id = post.json().get("id", 2)
    except:
        new_id = 2

    print(f"\n== PATCH /api/products/{new_id} ==")
    patch_body = {"price": 1999.0}
    patch = requests.patch(f"{BASE}/{new_id}", json=patch_body)
    print(patch.status_code, patch.text)

    del_id = new_id
    print(f"\n== DELETE /api/products/{del_id} ==")
    delete = requests.delete(f"{BASE}/{del_id}")
    print(delete.status_code, delete.text if delete.text else "")

if __name__ == "__main__":
    main()