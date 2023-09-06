# CURRENCY APP 
### project for the analysis of currencies

## Clone project

```
https://github.com/muhtor/currency_app.git
```

## Installation and running

### DOCKER
> Running migrations with docker-compose (if `run` is used instead of `exec`, then new container is created instead of using the existing one - hence it's better to use `exec`)

### Commands
```
docker compose exec cr_web python manage.py makemigrations
docker compose exec cr_web python manage.py migrate
docker compose exec cr_web python manage.py createsuperuser
```
if you want to go inside the container
```
docker exec -it cr_web bash
```
and you can easily run manage.py

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Caches

```
docker compose exec cr_web python manage.py createcachetable
```
or (inside the container)
```
python manage.py createcachetable
```
---


### Testing

```
docker compose exec cr_web python manage.py test api
```
or (inside the container)
```
python manage.py test api
```
---

### Load archive rates

> administrator has access to the management command for loading archive rates

```
docker compose exec cr_web 
```
or (inside the container)
```
python manage.py load_currency_history
```
---


### Other commands

Deleting all images and containers (dangerous please use it with caution)
```
docker system prune -a --volumes
```

```
docker images
docker container ls
```

## Documentations

- [SWAGGER](http://127.0.0.1:8888/swagger/) <br>
- [REDOC](http://127.0.0.1:8888/redoc/)
