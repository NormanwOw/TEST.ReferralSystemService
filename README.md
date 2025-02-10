# Referral System Service

![](https://img.shields.io/badge/Python-v3.10-green) ![](https://img.shields.io/badge/FastAPI-v0.115.8-blue) 
![](https://img.shields.io/badge/SQLAlchemy-v2.0-yellow) ![](https://img.shields.io/badge/PostgreSQL-v16-blue) 
![](https://img.shields.io/badge/Redis-v7.0-red) ![](https://img.shields.io/badge/Alembic-v2.0-violet) 
![](https://img.shields.io/badge/Docker-blue)


## Install
1. Изменить переменные окружения в deploy/.env (либо для теста можно оставить без изменения): 
2. `$ cd deploy && docker-compose up -d --build`

Swagger будет доступен по адресу: `127.0.0.1:8000/api/v1/docs`

## Tests

Актуальная версия запущена здесь - http://46.146.233.197:8000/api/v1/docs  
- Test login: **test@gmail.com**  
- Test password: **123**  

`user_id` для эндпоинта `GET /api/v1/users/{user_id}/referrals` можно получить в `GET /api/v1/auth/me`
после прохождения авторизации

