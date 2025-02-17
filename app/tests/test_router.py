import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from fastapi import status
from app.DAO.database import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
async def test_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        print("AsyncClient инициализирован")
        yield ac
        print("AsyncClient завершен")


@pytest.fixture
def generate_data():
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "confirm_password": "testpassword"
    }
    return user_data


@pytest.mark.asyncio
async def test_register_user(test_client, test_session):
    response = await test_client.post("/register/", json=generate_data())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message'] == "Вы успешно зарегестрированы!"


@pytest.mark.asyncio
async def test_register_existing_user(test_client, test_session):
    await test_client.post("/register/", json=generate_data())
    response = await test_client.post("/register/", json=generate_data())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_auth_user(test_client, test_session):
    await test_client.post("/register/", json=generate_data())
    auth_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = await test_client.post("/login/", json=auth_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_auth_with_wrong_password(test_client, test_session):
    await test_client.post('/register/', json=generate_data())
    auth_data_with_wrong_password = {
        "email": "test@example.com",
        "password": "testwrongpassword"
    }
    response = await test_client.post("/login/", json=auth_data_with_wrong_password)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout(test_client, test_session):
    response = await test_client.post("/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message'] == "Пользователь успешно вышел из системы"
