from httpx import AsyncClient

# ── helpers ──────────────────────────────────────────────────────────────────


async def _create_user(
    client: AsyncClient,
    email: str = "api_test@example.com",
    name: str = "API User",
) -> dict:
    resp = await client.post("/users", json={"email": email, "name": name})
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _create_task(
    client: AsyncClient,
    user_id: int,
    title: str = "Test task",
) -> dict:
    resp = await client.post(
        f"/users/{user_id}/tasks",
        json={"title": title},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── POST /users ───────────────────────────────────────────────────────────────


async def test_create_user_success(api_client: AsyncClient) -> None:
    resp = await api_client.post(
        "/users", json={"email": "create_user@example.com", "name": "Alice"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "create_user@example.com"
    assert data["name"] == "Alice"
    assert "id" in data
    assert "created_at" in data


async def test_create_user_duplicate_email_returns_409(api_client: AsyncClient) -> None:
    await _create_user(api_client, email="dup@example.com", name="First")

    resp = await api_client.post("/users", json={"email": "dup@example.com", "name": "Second"})

    assert resp.status_code == 409


async def test_create_user_invalid_email_returns_422(api_client: AsyncClient) -> None:
    resp = await api_client.post("/users", json={"email": "not-an-email", "name": "Bad"})

    assert resp.status_code == 422


async def test_create_user_empty_name_returns_422(api_client: AsyncClient) -> None:
    resp = await api_client.post("/users", json={"email": "valid@example.com", "name": ""})

    assert resp.status_code == 422


# ── GET /users/{id} ───────────────────────────────────────────────────────────


async def test_get_user_success(api_client: AsyncClient) -> None:
    created = await _create_user(api_client, email="getuser@example.com", name="Bob")
    user_id = created["id"]

    resp = await api_client.get(f"/users/{user_id}")

    assert resp.status_code == 200
    assert resp.json()["id"] == user_id


async def test_get_user_not_found_returns_404(api_client: AsyncClient) -> None:
    resp = await api_client.get("/users/999999")

    assert resp.status_code == 404


# ── POST /users/{id}/tasks ────────────────────────────────────────────────────


async def test_create_task_success(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="taskowner@example.com")

    resp = await api_client.post(
        f"/users/{user['id']}/tasks",
        json={"title": "Write tests", "description": "All cases"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Write tests"
    assert data["description"] == "All cases"
    assert data["status"] == "new"
    assert data["user_id"] == user["id"]


async def test_create_task_unknown_user_returns_404(api_client: AsyncClient) -> None:
    resp = await api_client.post(
        "/users/999999/tasks",
        json={"title": "Orphan"},
    )

    assert resp.status_code == 404


async def test_create_task_empty_title_returns_422(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="emptytitle@example.com")

    resp = await api_client.post(
        f"/users/{user['id']}/tasks",
        json={"title": ""},
    )

    assert resp.status_code == 422


# ── GET /users/{id}/tasks ─────────────────────────────────────────────────────


async def test_get_user_tasks_returns_list(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="listtasks@example.com")
    await _create_task(api_client, user["id"], "T1")
    await _create_task(api_client, user["id"], "T2")

    resp = await api_client.get(f"/users/{user['id']}/tasks")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_get_user_tasks_filter_by_status(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="filtertasks@example.com")
    await _create_task(api_client, user["id"], "New task")

    resp = await api_client.get(f"/users/{user['id']}/tasks", params={"status": "done"})

    assert resp.status_code == 200
    assert resp.json()["total"] == 0


# ── PATCH /tasks/{id}/status ──────────────────────────────────────────────────


async def test_update_task_status_success(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="statusupdate@example.com")
    task = await _create_task(api_client, user["id"], "Status task")

    resp = await api_client.patch(
        f"/tasks/{task['id']}/status",
        json={"status": "in_progress"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


async def test_update_task_status_invalid_transition_returns_422(
    api_client: AsyncClient,
) -> None:
    user = await _create_user(api_client, email="badtransition@example.com")
    task = await _create_task(api_client, user["id"], "Done task")

    await api_client.patch(f"/tasks/{task['id']}/status", json={"status": "in_progress"})
    await api_client.patch(f"/tasks/{task['id']}/status", json={"status": "done"})

    resp = await api_client.patch(f"/tasks/{task['id']}/status", json={"status": "new"})

    assert resp.status_code == 422


async def test_update_task_status_not_found_returns_404(api_client: AsyncClient) -> None:
    resp = await api_client.patch("/tasks/999999/status", json={"status": "in_progress"})

    assert resp.status_code == 404


# ── DELETE /tasks/{id} ────────────────────────────────────────────────────────


async def test_delete_task_success(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="deletetask@example.com")
    task = await _create_task(api_client, user["id"], "To delete")

    resp = await api_client.delete(f"/tasks/{task['id']}")

    assert resp.status_code == 200
    assert resp.json()["ok"] is True


async def test_delete_task_not_found_returns_404(api_client: AsyncClient) -> None:
    resp = await api_client.delete("/tasks/999999")

    assert resp.status_code == 404


# ── GET /users/{id}/tasks/stats ───────────────────────────────────────────────


async def test_get_task_stats_success(api_client: AsyncClient) -> None:
    user = await _create_user(api_client, email="stats_api@example.com")
    for i in range(3):
        await _create_task(api_client, user["id"], f"Task {i}")

    resp = await api_client.get(f"/users/{user['id']}/tasks/stats")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["new"] == 3
    assert data["in_progress"] == 0


async def test_get_task_stats_unknown_user_returns_404(api_client: AsyncClient) -> None:
    resp = await api_client.get("/users/999999/tasks/stats")

    assert resp.status_code == 404
