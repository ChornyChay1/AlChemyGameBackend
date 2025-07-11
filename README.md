# Серверная часть образовательной игры «Приключения алхимика»

## О проекте

«Приключения алхимика» — образовательная интерактивная игра по химии для средних классов.  
Серверная часть отвечает за авторизацию, хранение данных игроков, управление прогрессом, тестами и рейтингами.

---
## Описание серверной части

Основные функции сервера:
- Обработка запросов от клиента (React/TypeScript)
- Хранение данных в базе (SQLite с SQLAlchemy)
- Валидация данных с помощью Pydantic
- Асинхронная работа с FastAPI и запуск через Hypercorn для высокой производительности

Основные модули сервера:
- Модуль регистрации/авторизации
- Модуль прохождения и учета рейтинга
- Модуль обработки/передачи файлов 


---
## Быстрый старт

```bash
git clone https://github.com/ChornyChay1/AlchemyGameBackend.git
cd AlchemyGameBackend
pip install -r requirements.txt
hypercorn main:app --reload
```
API будет доступен по адресу: http://localhost:8000

---
## Используемые библиотеки

- [FastAPI](https://fastapi.tiangolo.com/) — веб-фреймворк для создания API  
- [Pydantic](https://pydantic.dev/) — валидация и сериализация данных  
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM для работы с базой данных  
- [Hypercorn](https://pgjones.gitlab.io/hypercorn/) — ASGI сервер для запуска приложения

---
## Связанный репозиторий

Frontend : [Frontend.](https://github.com/ChornyChay1/AlChemyGameFrontend)   

 
