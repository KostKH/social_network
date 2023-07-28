from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from business_layer.auth.authenticate import authenticate
from business_layer.auth.hash_password import HashPassword
from business_layer.auth.jwt_handler import create_access_token
from business_layer.schemas import LikeBase, PostCreate, UserCreate
from db_layer.db_engine import Base, get_async_session
from db_layer.models import Like, Post, User
from main import app

BASE_DIR = Path('.').absolute()
APP_DIR = BASE_DIR
TEST_DB_PATH = APP_DIR / 'network_db/test.db'
SQLALCHEMY_DATABASE_URL = f'sqlite+aiosqlite:///{TEST_DB_PATH}'


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=engine)


async def override_get_async_session():
    async with TestingSessionLocal() as session:
        await session.execute(text('PRAGMA foreign_keys = ON'))
        yield session


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


password_handler = HashPassword()
password_hash = password_handler.create_hash('testpassword123')

active_user1 = User(
    id=1,
    username='User1',
    password=password_hash,
    name='Виктор',
    surname='Тестовый1',
    email='aaa@bbb.ccc',
    is_active=True,
    is_superuser=False,
)

active_user2 = User(
    id=2,
    username='User2',
    password=password_hash,
    name='Виктор',
    surname='Тестовый2',
    email='aaa@bbb.ccc',
    is_active=True,
    is_superuser=False,
)
active_user3 = User(
    id=3,
    username='User3',
    password=password_hash,
    name='Виктор',
    surname='Тестовый3',
    email='aaa@bbb.ccc',
    is_active=True,
    is_superuser=False,
)
inactive_user = User(
    id=4,
    username='User4',
    password=password_hash,
    name='Виктор',
    surname='Тестовый4',
    email='aaa@bbb.ccc',
    is_active=False,
    is_superuser=False,
)
posts = [
    {
        'text': 'Тестовый пост1',
        'author_id': 1,
    },
    {
        'text': 'Тестовый пост2',
        'author_id': 1,
    },
    {
        'text': 'Тестовый пост3',
        'author_id': 1,
    },
]
likes = [
    {
        'post_id': 1,
        'liker_id': 2,
    },
    {
        'post_id': 1,
        'liker_id': 3,
    },
    {
        'post_id': 2,
        'liker_id': 2,
    },
]


async def create_user(userdata):
    async with TestingSessionLocal() as session:
        await session.execute(text('PRAGMA foreign_keys = ON'))
        user_schema = UserCreate(**userdata.__dict__)
        prepared_data = user_schema.dict()
        user = User(**prepared_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        token = create_access_token(user.id)
        return user, token


@pytest_asyncio.fixture
async def create_users():
    tempusers = {}
    tempusers['active_user1'] = await create_user(active_user1)
    tempusers['active_user2'] = await create_user(active_user2)
    tempusers['active_user3'] = await create_user(active_user3)
    tempusers['inactive_user'] = await create_user(inactive_user)
    return tempusers


@pytest_asyncio.fixture
async def posts_in_db(create_users):
    async with TestingSessionLocal() as session:
        await session.execute(text('PRAGMA foreign_keys = ON'))
        created_posts = []
        for postdata in posts:
            post_schema = PostCreate(**postdata)
            prepared_data = post_schema.dict()
            post = Post(**prepared_data)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            created_posts.append(post.__dict__.copy())
        return created_posts, create_users


@pytest_asyncio.fixture
async def posts_likes_in_db(posts_in_db):
    async with TestingSessionLocal() as session:
        await session.execute(text('PRAGMA foreign_keys = ON'))
        created_likes = []
        for likedata in likes:
            like_schema = LikeBase(**likedata)
            prepared_data = like_schema.dict()
            like = Like(**prepared_data)
            session.add(like)
            await session.commit()
            await session.refresh(like)
            created_likes.append(like.__dict__.copy())
        return created_likes, posts_in_db


def override_failed_auth():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=('Для получения доступа авторизуйтейсь '
                'и добавьте токен в запрос.'))


@pytest.fixture
def active_client1():
    app.dependency_overrides = {}
    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[authenticate] = lambda: active_user1
    with TestClient(app) as client:
        yield client


@pytest.fixture
def active_client2():
    app.dependency_overrides = {}
    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[authenticate] = lambda: active_user2
    with TestClient(app) as client:
        yield client


@pytest.fixture
def active_client3():
    app.dependency_overrides = {}
    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[authenticate] = lambda: active_user3
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_client():
    app.dependency_overrides = {}
    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[authenticate] = override_failed_auth
    with TestClient(app) as client:
        yield client
