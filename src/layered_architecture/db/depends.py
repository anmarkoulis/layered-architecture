from layered_architecture.db.session import async_session


async def get_db() -> async_session:
    db = async_session()
    try:
        yield db
    finally:
        await db.close()
