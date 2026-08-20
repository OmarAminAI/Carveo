import asyncio
import selectors
import sys

from carveo_core.database import create_engine, create_session_factory
from carveo_core.seed import seed_fixtures

from carveo_api.settings import get_settings


async def run() -> None:
    engine = create_engine(get_settings().database_url)
    factory = create_session_factory(engine)
    async with factory() as session:
        await seed_fixtures(session)
    await engine.dispose()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.run(run(), loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()))
    else:
        asyncio.run(run())
