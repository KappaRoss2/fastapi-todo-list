1. В директорию src нужно добавить 2 файла .env и db.env, содержимое файлов:
    .env:
        - DEBUG=Дебаг режим(True/False)
        - CRYPT_CONTEXT_SCHEMA=Схема шифрования для библиотеки bcrypt(bcrypt)
        - CRYPT_CONTEXT_DEPRECATED=Режим шифрования(auto)
        - REDIS_BROKER=Брокер(redis://redis:6379/0)
        - REDIS_BACKEND=Вывод результата(redis://redis:6379/0)
        - SMTP_SERVER=SMTP сервер(smtp.mail.ru)
        - SMTP_PORT=SMTP порт(587)
        - SMTP_PASSWORD=SMTP пароль
        - SMTP_USERNAME=SMTP почта с которой будете слать сообщения
        - SECRET_KEY=Секретный ключ для шифрования
        - ALGORITHM=Алгоритм хэширования
        - ACCESS_TOKEN_EXPIRE_MINUTES=Время протухания токена в минутах(1440)
        - TEST_BASE_URL=Базовый URL для тестов (http://localhost:8000)
    db.env:
        - POSTGRES_HOST=Хост сервера БД
        - POSTGRES_PORT=Порт сервера БД
        - POSTGRES_DB=Имя БД
        - POSTGRES_USER=Имя пользователя
        - POSTGRES_PASSWORD=Пароль пользователя
        - POSTGRES_TEST_DB=Имя БД для тестов

2. Перейти в директорию deploy.
3. Ввести команду docker-compose build, дождаться окончания выполнения.
4. Ввести команду docker-compose up -d, дождаться когда все контейнеры поднимуться.
5. Перейти в консоль контейнера с именем server.
6. Создать миграции командой alembic revision --autogenerate -m "Текст миграции".
7. Применить миграции alembic upgrade head.
