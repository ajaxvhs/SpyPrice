import uuid
import pytest
import pytest_asyncio


pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture(loop_scope="session")
async def product(client):
    r = await client.post("/produtos", json={"name": "Test Product"})
    return r.json()


class TestCreateLink:
    async def test_create_valid(self, client, product):
        pid = product["id"]
        r = await client.post(
            f"/produtos/{pid}/links",
            json={"marketplace": "Shopee", "url": "https://shopee.com.br/item"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["marketplace"] == "Shopee"
        assert data["url"] == "https://shopee.com.br/item"
        assert data["product_id"] == pid
        assert uuid.UUID(data["id"])

    async def test_create_duplicate_url(self, client, product):
        pid = product["id"]
        payload = {"marketplace": "Shopee", "url": "https://shopee.com.br/item"}
        await client.post(f"/produtos/{pid}/links", json=payload)
        r = await client.post(f"/produtos/{pid}/links", json=payload)
        assert r.status_code == 409

    async def test_create_product_not_found(self, client):
        r = await client.post(
            f"/produtos/{uuid.uuid4()}/links",
            json={"marketplace": "Shopee", "url": "https://shopee.com.br/item"},
        )
        assert r.status_code == 404

    async def test_create_invalid_body(self, client, product):
        r = await client.post(f"/produtos/{product['id']}/links", json={})
        assert r.status_code == 422


class TestListLinks:
    async def test_list_empty(self, client, product):
        r = await client.get(f"/produtos/{product['id']}/links")
        assert r.status_code == 200
        assert r.json() == []

    async def test_list_with_links(self, client, product):
        pid = product["id"]
        await client.post(
            f"/produtos/{pid}/links",
            json={"marketplace": "ML", "url": "https://mercadolivre.com.br/item"},
        )
        await client.post(
            f"/produtos/{pid}/links",
            json={"marketplace": "Shopee", "url": "https://shopee.com.br/item"},
        )
        r = await client.get(f"/produtos/{pid}/links")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        assert data[0]["product_id"] == pid

    async def test_list_product_not_found(self, client):
        r = await client.get(f"/produtos/{uuid.uuid4()}/links")
        assert r.status_code == 200
        assert r.json() == []


class TestUpdateLink:
    async def test_update_valid(self, client, product):
        pid = product["id"]
        created = await client.post(
            f"/produtos/{pid}/links",
            json={"marketplace": "Shopee", "url": "https://shopee.com.br/old"},
        )
        link_id = created.json()["id"]
        r = await client.put(
            f"/links/{link_id}",
            json={"marketplace": "ML", "url": "https://mercadolivre.com.br/new"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["marketplace"] == "ML"
        assert data["product_id"] == pid

    async def test_update_not_found(self, client):
        r = await client.put(
            f"/links/{uuid.uuid4()}",
            json={"marketplace": "ML", "url": "https://mercadolivre.com.br/item"},
        )
        assert r.status_code == 404


class TestDeleteLink:
    async def test_delete_existing(self, client, product):
        pid = product["id"]
        created = await client.post(
            f"/produtos/{pid}/links",
            json={"marketplace": "Shopee", "url": "https://shopee.com.br/item"},
        )
        link_id = created.json()["id"]
        r = await client.delete(f"/links/{link_id}")
        assert r.status_code == 204

        r = await client.get(f"/produtos/{pid}/links")
        assert len(r.json()) == 0

    async def test_delete_not_found(self, client):
        r = await client.delete(f"/links/{uuid.uuid4()}")
        assert r.status_code == 404
