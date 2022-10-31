# Foodgram
![Foodgram workflow](https://github.com/ifize/foodgram-project-react/actions/workflows/main.yml/badge.svg)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## О проекте:
Сайт Foodgram, "Продуктовый помощник". На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
- Проект доступен тут: http://158.160.9.25
- "Админка" http://158.160.9.25/admin/ (логин: a@a.ru пароль: admin)

## Запуск проекта на локальной машине:

Клонировать репозиторий:
```
git@github.com:ifize/foodgram-project-react.git
```

В директории infra создать файл .env и заполнить такими данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='SECRET_KEY'
```
Создать и запустить контейнеры Docker, выполнив следующую команду в папке infra
```
docker-compose -f docker-compose-local.yml up -d
```
Подготовить миграции (если их нет)
```
docker-compose -f docker-compose-local.yml exec backend python manage.py makemigrations
```
Произвести миграции (если их нет)
```
docker-compose -f docker-compose-local.yml exec backend python manage.py migrate
```
Создать суперпользователя (если его нет)
```
docker-compose -f docker-compose-local.yml exec backend python manage.py createsuperuser
```
После наполнения БД рецептами
```
docker-compose -f docker-compose-local.yml exec backend python manage.py createsuperuser
```
Перейти в режим логов следующей командой
```
docker-compose -f docker-compose-local.yml logs -f
```
При подключении базы данных Postgress, развернутую в контейнере, указать следующие параметры
- Host: ```localhost```
- Port: ```5432```
- User: ```POSTGRES_USER из .env```
- Password: ```POSTGRES_PASSWORD из .env```

После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)

Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)

Админка будет доступна по адресу: [http://localhost/admin/](http://localhost/admin/)

## Порядок развертывания проекта на удаленном сервере:

Клонировать репозиторий:
```
git@github.com:ifize/foodgram-project-react.git
```

Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop) 
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Установите [Docker Compose](https://docs.docker.com/compose/install/)

Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp infra/docker-compose.yaml <username>@<IP>:/home/<username>/
scp -r infra/nginx.conf <username>@<IP>:/home/<username>/
```

Создать и запустить контейнеры Docker, выполнить команду на сервере
*(версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):*
```
sudo docker-compose -f docker-compose-prod.yml up -d
```

После успешной сборки выполнить миграции:
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```
sudo docker-compose exec backend python manage.py collectstatic --noinput
```

Наполнить базу данных индигриентами из файла ingredients.json:
```
sudo docker-compose exec backend python manage.py loaddata ingredients.json
```

Создать тэги в БД с помощью management command import_tags:
```
sudo docker-compose exec backend python manage.py import_tags
```


Для пересборки контейнеров:
```
sudo docker-compose up -d --build
```

Для остановки контейнеров Docker:
```
sudo docker-compose down -v      # с удалением контейнеров, образов, сетей (network), томов (volume) в том числе с данными локальной БД
sudo docker-compose stop         # без удаления вышеперечисленного
```

Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # пароль, если ssh защищен
SSH_KEY                 # приватный ssh-ключ
DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение
```

### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### *Бэкенд разработал:*
[Илья воронков](https://github.com/ifize)
