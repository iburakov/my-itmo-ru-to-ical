# ITMO schedule to iCalendar converter

Сервис, который ходит на my.itmo.ru за расписанием и экспортирует его как iCalendar с публичной ссылкой. Позволяет автоматически и с автообновлением экспортировать пары в календари Google, iCloud и другие.

## Что нужно

Логин и пароль от ИСУ, поэтому безопасности ради захостить себе сервис придётся самостоятельно.

Нужен **личный** сервер (без доступа посторонних) с `docker` на нём.

## Как завести

1. Подставить username/password в команду и запустить контейнер:

   ```bash
   APP_PORT=35601

   docker run -d \
   	--restart=unless-stopped \
   	--name itmo_ical \
   	-p=$APP_PORT:35601 \
   	-e ITMO_ICAL_ISU_USERNAME=100000 \
   	-e ITMO_ICAL_ISU_PASSWORD=XXXXXXXXXXXXX \
   	ghcr.io/iburakov/my-itmo-ru-to-ical
   ```

2. Получить публичную ссылку на .ics:

   ```bash
   URL_PATH=$(docker logs itmo_ical 2>&1 | grep -oh '/calendar/.*')
   HOST_IP=$(curl -s ipinfo.io/ip)

   echo "http://$HOST_IP:$APP_PORT$URL_PATH"

   # should look like
   # http://93.184.216.34:35601/calendar/gnKZT88jeuKDdhh7Ow8mwsAbMpIyVKaCBpl2CtqJqYI
   ```

3. Если по ссылке скачивается .ics файл, всё работает
4. Импортировать ссылку в свой календарь. Он будет периодически повторять запрос для получения обновлений - изменяющиеся аудитории теперь не беда ;)

PS. Ссылка содержит хеш имени пользователя и пароля, чтобы она была и неподбираемой для посторонних, и относительно постоянной без использования какого-либо хранилища. Стоит иметь в виду, что меняется username/password - меняется ссылка.

## Опциональное

Из коробки поддерживается мониторинг ошибок с помощью [Sentry](https://sentry.io/). Можно создать проект (Python/Flask) и передать [DSN](https://docs.sentry.io/product/sentry-basics/dsn-explainer/) в переменную окружения `ITMO_ICAL_SENTRY_DSN` при старте контейнера.
