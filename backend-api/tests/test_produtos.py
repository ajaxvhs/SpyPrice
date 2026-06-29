import uuid
import pytest


pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestListProducts:
    async def test_empty_list(self, client):
        r = await client.get("/produtos")
        assert r.status_code == 200
        assert r.json() == []

    async def test_pagination_defaults(self, client):
        r = await client.get("/produtos?limit=50&offset=0")
        assert r.status_code == 200

    async def test_limit_exceeds_max(self, client):
        r = await client.get("/produtos?limit=51")
        assert r.status_code == 422


class TestCreateProduct:
    async def test_create_valid(self, client):
        r = await client.post("/produtos", json={"name": "Test Product"})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Test Product"
        assert uuid.UUID(data["id"])

    async def test_create_name_too_short(self, client):
        r = await client.post("/produtos", json={"name": "a"})
        assert r.status_code == 422

    async def test_create_missing_name(self, client):
        r = await client.post("/produtos", json={})
        assert r.status_code == 422


class TestGetProduct:
    async def test_get_existing(self, client):
        created = await client.post("/produtos", json={"name": "My Product"})
        pid = created.json()["id"]

        r = await client.get(f"/produtos/{pid}")
        assert r.status_code == 200
        assert r.json()["name"] == "My Product"

    async def test_get_not_found(self, client):
        r = await client.get(f"/produtos/{uuid.uuid4()}")
        assert r.status_code == 404


class TestUpdateProduct:
    async def test_update_name(self, client):
        created = await client.post("/produtos", json={"name": "Old Name"})
        pid = created.json()["id"]

        r = await client.put(f"/produtos/{pid}", json={"name": "New Name"})
        assert r.status_code == 200
        assert r.json()["name"] == "New Name"

    async def test_update_not_found(self, client):
        r = await client.put(f"/produtos/{uuid.uuid4()}", json={"name": "Any"})
        assert r.status_code == 404


class TestDeleteProduct:
    async def test_delete_existing(self, client):
        created = await client.post("/produtos", json={"name": "To Delete"})
        pid = created.json()["id"]

        r = await client.delete(f"/produtos/{pid}")
        assert r.status_code == 204

        r = await client.get(f"/produtos/{pid}")
        assert r.status_code == 404

    async def test_delete_not_found(self, client):
        r = await client.delete(f"/produtos/{uuid.uuid4()}")
        assert r.status_code == 404
