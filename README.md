# social_network


`social_network` - REST API социальной сети с возможностью делать посты и ставить лайки постам других пользователей.

## Документация
После запуска сервиса документация по API будет доступна по ссылкам:
- `<host_address>:8000/docs/`
- `<host_address>:8000/redoc/`


## Системные требования
- Python 3.11+
- Works on Linux, Windows, macOS

## Основные технологии:
- Python 3.11
- FastAPI
- SQLite
- SQLAlchemy
- Alembic 
- Uvicorn
- Pytest

## Как запустить проект:


Необходимо выполнить следующие шаги:
- Склонируйте репозиторий с GitHub:
```
git clone git@github.com:KostKH/social_network.git
cd social_network
```
- Создайте и активируйте виртуальное окружение, установите зависимости:
```
python -m venv venv

source venv/bin/activate <<< используйте эту команду, если у вас Linux
source venv/scripts/activate <<< используйте эту команду, если у вас Windows

pip install -r requirements.txt
```
- Сгенерируйте свой секретный ключ для `FastAPI`. Это можно сделать, например, введя в терминале `bash` такую команду:
```
grep -ao '[a-zA-Z0-9]' < /dev/urandom | head -24 | tr -d '\n'
```
- Cоздайте в папке `social_network` файл `.env` с переменными окружения. Можно создать его из вложенного образца `env_example.env`:
```
cp env_example.env .env
```
- Откройте файл .env в редакторе и поменяйте, при необходимости, переменные окружения. При этом обязательно поменяйте секретный ключ `JWT_SECRET_KEY` на значение, которое вы сгенерировали на предыдущем шаге:
```
DATABASE_URL='sqlite+aiosqlite:///network_db/network.db'
JWT_SECRET_KEY=some_secret_key
JWT_ALGORITHM=HS256
JWT_EFFECT_SECONDS=86400

```
- Запустите приложение:
```
uvicorn main:app
```
После запуска API будет доступно по адресу: `http://<host address>:8000/api/v1/users/signup`

Документация по API будет доступна по  адресам:
- `<host_address>:8000/docs/`
- `<host_address>:8000/redoc/`


Если вы хотите протестировать приложение, то тогда, находясь в папке `social_network`, запустите команду `pytest`.

## О программе:

Автор: Константин Харьков