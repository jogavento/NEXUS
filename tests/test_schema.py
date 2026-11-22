import aiosqlite
import pytest
from nexus.database import SCHEMA
from nexus.repositories import Repository

@pytest.mark.asyncio
async def test_world_and_inventory_persist():
    db = await aiosqlite.connect(":memory:")
    db.row_factory = aiosqlite.Row
    await db.executescript(SCHEMA)
    repo = Repository(db)
    world = await repo.create_world(111,"Test Realm")
    assert world["name"] == "Test Realm"
    await repo.add_resource(111,222,"wood",9)
    citizen, inventory = await repo.profile(111,222)
    assert citizen["level"] == 1
    assert inventory["wood"] == 9
    await db.close()
