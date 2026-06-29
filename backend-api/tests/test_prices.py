import uuid
import pytest
import pytest_asyncio


pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture(loop_scope="session")
async def link(client):
    rp = await client.post("/produtos", json={"name": "Test Product"})
    pid = rp.json()["id"]
    rl = await client.post(
        f"/produtos/{pid}/links",
        json={"marketplace": "Shopee", "url": "https://shopee.com.br/item"},
    )
    return rl.json()


class TestCreatePrice:
    async def test_create_valid(self, client, link):
        r = await client.post(
            f"/links/{link['id']}/precos",
            json={"price": 99.90, "is_available": True},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["price"] == 99.90
        assert data["is_available"] is True
        assert data["link_id"] == link["id"]
        assert uuid.UUID(data["id"])

    async def test_create_default_availability(self, client, link):
        r = await client.post(
            f"/links/{link['id']}/precos",
            json={"price": 49.99},
        )
        assert r.status_code == 201
        assert r.json()["is_available"] is True

    async def test_create_link_not_found(self, client):
        r = await client.post(
            f"/links/{uuid.uuid4()}/precos",
            json={"price": 10.0},
        )
        assert r.status_code == 404

    async def test_create_invalid_price(self, client, link):
        r = await client.post(
            f"/links/{link['id']}/precos",
            json={"price": -1},
        )
        assert r.status_code == 422

    async def test_create_invalid_body(self, client, link):
        r = await client.post(f"/links/{link['id']}/precos", json={})
        assert r.status_code == 422


class TestListPrices:
    async def test_list_empty(self, client, link):
        r = await client.get(f"/links/{link['id']}/precos")
        assert r.status_code == 200
        assert r.json() == []

    async def test_list_with_prices(self, client, link):
        lid = link["id"]
        await client.post(f"/links/{lid}/precos", json={"price": 10.0})
        await client.post(f"/links/{lid}/precos", json={"price": 20.0})
        r = await client.get(f"/links/{lid}/precos")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        assert data[0]["link_id"] == lid

    async def test_list_order(self, client, link):
        lid = link["id"]
        await client.post(f"/links/{lid}/precos", json={"price": 10.0})
        await client.post(f"/links/{lid}/precos", json={"price": 20.0})
        r = await client.get(f"/links/{lid}/precos")
        data = r.json()
        assert data[0]["price"] == 20.0
        assert data[1]["price"] == 10.0
