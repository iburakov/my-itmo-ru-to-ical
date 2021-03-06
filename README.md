# ITMO schedule to iCalendar converter

Сервис, который ходит на my.itmo.ru за расписанием и экспортирует его как iCalendar с публичной ссылкой. Позволяет автоматически и с автообновлением экспортировать пары в календари Google, iCloud и другие.

## Пререквизиты

К сожалению, нужен логин и пароль от ИСУ, поэтому безопасности ради публичного сервиса не будет.
Понадобится:

- сервер с публичным IP адресом;
- `git`, `docker`, `docker-compose` в нём.

## Как запустить
1. 	Склонировать репозиторий:
	```bash
	git clone https://github.com/iburakov/my-itmo-ru-to-ical.git && cd my-itmo-ru-to-ical
	```
1. Заполнить конфиг:
	```bash
	cp config/config.py.template config/config.py && vim config/config.py
	```
1. Запустить сервис: `docker-compose up -d`
1. Достать ссылку из логов: `docker-compose logs | grep "path for calendar"`
1. Собрать ссылку: `http://<ip/domain сервера>:35601<path>`
1. Если по ссылке скачивается .ics файл, всё работает
1. Импортировать ссылку в свой календарь
1. ???
1. PROFIT!!!

PS. Ссылка содержит хеш имени пользователя и пароля. Меняются данные - меняется ссылка.

PPPS. Если вдруг стандартный порт порт занят, поправьте первый порт в `docker-compose.yml` на свободный.
