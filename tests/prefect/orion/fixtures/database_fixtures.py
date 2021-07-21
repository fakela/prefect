import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from prefect.orion.utilities.database import Base
from prefect.orion.utilities.settings import Settings
from prefect.orion import models, schemas


@pytest.fixture
async def database_engine():
    """Creates an in memory sqlite database for use in testing"""
    # create an in memory db engine
    engine = create_async_engine("sqlite+aiosqlite://", echo=Settings().database.echo)

    # populate database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine


@pytest.fixture
async def database_session(database_engine):
    """Test database session"""
    async with AsyncSession(
        database_engine, future=True, expire_on_commit=False
    ) as session:
        # open transaction
        async with session.begin():
            yield session


@pytest.fixture
async def flow(database_session):
    return await models.flows.create_flow(
        session=database_session, flow=schemas.inputs.FlowCreate(name="my-flow")
    )


@pytest.fixture
async def flow_run(database_session, flow):
    return await models.flow_runs.create_flow_run(
        session=database_session,
        flow_run=schemas.inputs.FlowRunCreate(flow_id=flow.id, flow_version="0.1"),
    )