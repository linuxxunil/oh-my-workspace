"""S2 验收：AC3 登录+RBAC / AC4 用户+权限管理（REQ-001）。"""

from tests.conftest import auth_headers, login


def test_unauthenticated_returns_401(client):
    r = client.get("/users")
    assert r.status_code == 401


def test_wrong_password_returns_401(client):
    r = client.post("/auth/login", json={"email": "root@example.com", "password": "Wrong12345"})
    assert r.status_code == 401


def test_member_forbidden_on_user_mgmt(client):
    token = login(client, "member")
    r = client.get("/users", headers=auth_headers(token))
    assert r.status_code == 403


def test_admin_can_crud_member_but_not_touch_super_admin(client):
    admin = auth_headers(login(client, "admin"))
    # create member
    r = client.post(
        "/users",
        headers=admin,
        json={"email": "n1@example.com", "password": "Pass12345", "role": "member"},
    )
    assert r.status_code == 201, r.text
    uid = r.json()["id"]
    # admin 不可授 super_admin
    r = client.post(
        "/users",
        headers=admin,
        json={"email": "evil@example.com", "password": "Pass12345", "role": "super_admin"},
    )
    assert r.status_code == 403
    # admin 不可删 super_admin：先找到 root
    users = client.get("/users", headers=admin).json()
    root = next(u for u in users if u["role"] == "super_admin")
    r = client.delete(f"/users/{root['id']}", headers=admin)
    assert r.status_code == 403
    # admin 可删自己建的 member
    r = client.delete(f"/users/{uid}", headers=admin)
    assert r.status_code == 204


def test_super_admin_can_assign_permissions(client):
    root = auth_headers(login(client, "super_admin"))
    r = client.get("/permissions", headers=root)
    assert r.status_code == 200 and len(r.json()) >= 9
    r = client.put(
        "/roles/member/permissions",
        headers=root,
        json={"permission_codes": ["workflows:read", "workflows:run"]},
    )
    assert r.status_code == 200
    assert r.json()["permission_codes"] == ["workflows:read", "workflows:run"]


def test_admin_cannot_write_permissions(client):
    admin = auth_headers(login(client, "admin"))
    r = client.put(
        "/roles/member/permissions",
        headers=admin,
        json={"permission_codes": ["workflows:read"]},
    )
    assert r.status_code == 403
