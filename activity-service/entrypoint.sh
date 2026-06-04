@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume_events())
    yield
