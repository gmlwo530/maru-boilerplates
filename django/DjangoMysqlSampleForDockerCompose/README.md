# Django Mysql Sample for Docker Compose

## What you know commands

### Delete docker volume

```bash
$ docker volume rm django_sample_db_dev
```

## TODO

Execute command to "Grant privileges to DB_USER" when the first time the `docker-compose up` is executed.

```bash
mysql> create user 'test'@'%' identified by 'test1234';
Query OK, 0 rows affected (0.00 sec)
mysql> grant all privileges on test_database.* to test@'%';
Query OK, 0 rows affected (0.00 sec)
```
