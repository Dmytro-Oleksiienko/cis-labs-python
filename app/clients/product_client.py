import time
from typing import Optional, Any, Dict, List

import requests

BASE_URL = "http://localhost:8000/api/products"
SESSION = requests.Session()


def main() -> None:
    wait_for_server()

    while True:
        print("\n=== Product REST API Console Client (Python) ===")
        print("1. Отримати всі товари")
        print("2. Отримати товар за ID")
        print("3. Додати новий товар")
        print("4. Оновити товар (PUT)")
        print("5. Часткове оновлення (PATCH)")
        print("6. Видалити товар")
        print("0. Вийти")
        choice_str = input("Виберіть дію: ").strip()

        if not choice_str:
            continue

        try:
            choice = int(choice_str)
        except ValueError:
            print("Невірний вибір")
            continue

        try:
            if choice == 1:
                get_all()
            elif choice == 2:
                get_by_id()
            elif choice == 3:
                create()
            elif choice == 4:
                update_put()
            elif choice == 5:
                update_patch()
            elif choice == 6:
                delete()
            elif choice == 0:
                print("До зустрічі 👋")
                break
            else:
                print("Невірний вибір")
        except Exception as e:
            print(f"❌ Помилка: {e}")

def get_all() -> None:
    resp = SESSION.get(BASE_URL)
    if resp.status_code != 200:
        print(f"❌ Помилка: HTTP {resp.status_code}")
        print_error(resp)
        return

    products: List[Dict[str, Any]] = resp.json()
    print("\n--- Список товарів ---")
    for p in products:
        pid = p.get("id")
        name = safe(p.get("name"))
        price = p.get("price") or 0.0
        country = safe(p.get("country"))
        manufacturer = safe(p.get("manufacturer"))
        color = safe(p.get("color"))

        print(f"{pid:<4} | {name:<20} | {price:<8.2f} | {country:<10} | {manufacturer:<10} | {color:<8}")


def get_by_id() -> None:
    pid = read_long("ID товару: ")
    url = f"{BASE_URL}/{pid}"
    resp = SESSION.get(url)

    if resp.status_code != 200:
        print(f"❌ Помилка: HTTP {resp.status_code}")
        print_error(resp)
        return

    print("\n--- Товар ---")
    from pprint import pprint
    pprint(resp.json())


def create() -> None:
    print("\n--- Створення товару ---")

    dto: Dict[str, Any] = {
        "name": read_optional("Назва"),
        "manufacturer": read_optional("Виробник"),
        "country": read_optional("Країна"),
        "color": read_optional("Колір"),
        "price": read_optional_double("Ціна"),
        "storage": read_optional("Пам'ять / обсяг сховища"),
        "screenSize": read_optional("Діагональ екрану"),
        "imageUrl": read_optional("Посилання на зображення"),
    }

    print("\nВідправляю JSON:")
    from pprint import pprint
    pprint(dto)

    body = {k: v for k, v in dto.items() if v is not None}

    send_json(BASE_URL, "POST", body, print_response=True)


def update_put() -> None:
    print("\n--- Оновлення товару (PUT) ---")
    pid = read_long("ID товару: ")

    dto: Dict[str, Any] = {
        "name": read_optional("Нова назва"),
        "manufacturer": read_optional("Новий виробник"),
        "country": read_optional("Нова країна"),
        "color": read_optional("Новий колір"),
        "price": read_optional_double("Нова ціна"),
        "storage": read_optional("Нова пам'ять / обсяг сховища"),
        "screenSize": read_optional("Нова діагональ екрану"),
        "imageUrl": read_optional("Нове посилання на зображення"),
    }

    print("\nВідправляю JSON:")
    from pprint import pprint
    pprint(dto)

    body = {k: v for k, v in dto.items() if v is not None}

    send_json(f"{BASE_URL}/{pid}", "PUT", body, print_response=True)


def update_patch() -> None:
    print("\n--- Часткове оновлення товару (PATCH) ---")
    pid = read_long("ID товару: ")

    field = input("Поле для оновлення: ").strip()
    value = input("Нове значення: ").strip()

    if not field or not value:
        print("⚠️ Поля не можуть бути порожніми")
        return

    json_value: Any
    if field == "price":
        json_value = try_parse_double(value)
    else:
        json_value = value

    body = {field: json_value}

    print("\nВідправляю JSON:")
    from pprint import pprint
    pprint(body)

    send_json(f"{BASE_URL}/{pid}", "PATCH", body, print_response=True)


def delete() -> None:
    print("\n--- Видалення товару ---")
    pid = read_long("ID товару: ")
    resp = SESSION.delete(f"{BASE_URL}/{pid}")
    print(f"HTTP статус: {resp.status_code}")
    if resp.status_code == 204:
        print("✅ Товар видалено")
    else:
        print("❌ Помилка:")
        print_error(resp)

def send_json(url: str, method: str, body: Dict[str, Any], print_response: bool = True) -> None:
    method = method.upper()
    if method == "POST":
        resp = SESSION.post(url, json=body)
    elif method == "PUT":
        resp = SESSION.put(url, json=body)
    elif method == "PATCH":
        resp = SESSION.patch(url, json=body)
    else:
        raise ValueError(f"Непідтримуваний метод: {method}")

    print("HTTP статус:", resp.status_code)

    if print_response:
        try:
            print(resp.json())
        except Exception:
            print(resp.text)


def print_error(resp: requests.Response) -> None:
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

def safe(s: Optional[str]) -> str:
    return s if s is not None else "-"


def read_long(label: str) -> int:
    while True:
        val = input(label).strip()
        try:
            return int(val)
        except ValueError:
            print("Введіть коректне число.")


def read_optional(label: str) -> Optional[str]:
    val = input(f"{label} (enter щоб пропустити): ").strip()
    return val or None


def read_optional_double(label: str) -> Optional[float]:
    val = input(f"{label} (enter щоб пропустити): ").strip()
    if not val:
        return None
    try:
        d = float(val)
        if d < 0:
            print("⚠️ Ціна не може бути від'ємною, поле пропущено.")
            return None
        return d
    except ValueError:
        print("⚠️ Невірне число, поле пропущено.")
        return None


def try_parse_double(s: str) -> Optional[float]:
    try:
        return float(s)
    except ValueError:
        return None

def wait_for_server() -> None:
    url = BASE_URL
    attempts = 30
    print(f"Очікую запуск сервера на {url} ...")

    for _ in range(attempts):
        try:
            resp = SESSION.get(url, timeout=0.8)
            if 200 <= resp.status_code < 500:
                print("✅ Сервер доступний. Запускаємо клієнтське меню.")
                return
        except Exception:
            pass
        time.sleep(1.0)

    print("⚠️ Не вдалось дочекатися сервера. Переконайся, що FastAPI застосунок запущений.")


if __name__ == "__main__":
    main()