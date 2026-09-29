"""S2B 验收：AC2 管理员重置 / AC3 本人自改（REQ-004）。"""

from tests.conftest import auth_headers, login


def _login(client, email: str, password: str) -> int:
    return client.post("/auth/login", json={"email": email, "password": password}).status_code


def test_self_change_password_all_roles(client):
    for role, email, old in (
        ("super_admin", "root@example.com", "Root12345"),
        ("admin", "admin@example.com", "Admin12345"),
        ("member", "member@example.com", "Member12345"),
    ):
        me = auth_headers(login(client, role))
        # 未登录 → 401
        r = client.post("/auth/password", json={"old_password": old, "new_password": "New12345"})
        assert r.status_code == 401
        # 旧密码错 → 400；过短新密码 → 422
        r = client.post(
            "/auth/password", headers=me, json={"old_password": "Wrong12345", "new_password": "New12345"}
        )
        assert r.status_code == 400
        r = client.post("/auth/password", headers=me, json={"old_password": old, "new_password": "short"})
        assert r.status_code == 422
        # 自改成功：新密码 200，旧密码 401
        r = client.post("/auth/password", headers=me, json={"old_password": old, "new_password": "New12345"})
        assert r.status_code == 204, r.text
        assert _login(client, email, "New12345") == 200
        assert _login(client, email, old) == 401


def test_admin_reset_member_password(client):
    root = auth_headers(login(client, "super_admin"))
    r = client.post(
        "/users",
        headers=root,
        json={"email": "rst@example.com", "password": "Pass12345", "role": "member"},
    )
    assert r.status_code == 201, r.text
    uid = r.json()["id"]
    # member 自管他人 → 403（users:write 门）
    member = auth_headers(login(client, "member"))
    r = client.patch(f"/users/{uid}", headers=member, json={"password": "Hacked123"})
    assert r.status_code == 403
    # admin 重置他人 → 204，新密码可登录
    admin = auth_headers(login(client, "admin"))
    r = client.patch(f"/users/{uid}", headers=admin, json={"password": "Reset12345"})
    assert r.status_code == 200, r.text
    assert _login(client, "rst@example.com", "Reset12345") == 200
    assert _login(client, "rst@example.com", "Pass12345") == 401
    # admin 动 super_admin → 403（红线）
    super_id = client.get("/users", headers=root).json()
    sid = next(u["id"] for u in super_id if u["role"] == "super_admin")
    r = client.patch(f"/users/{sid}", headers=admin, json={"password": "Hacked123"})
    assert r.status_code == 403
