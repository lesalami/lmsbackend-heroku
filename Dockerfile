ARG PYTHON_VERSION=3.11-alpine

FROM python:${PYTHON_VERSION}
LABEL maintainer="Tonny-Bright Sogli"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY "CpB4dp4snAi4gIwmuvmUGHNETK2D6yBlOmnpnpV6lQwWPAfQXy"
ENV ALLOWED_HOSTS=*,0.0.0.0,
ENV EMAIL_HOST=smtp.gmail.com
ENV EMAIL_HOST_USER=brightonplace18@gmail.com
ENV EMAIL_HOST_PASSWORD=jditpcvodlazmikr
ENV FRONTEND_BASE_URL=http://localhost:3000
ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_STORAGE_BUCKET_NAME=HHAcademy_test
ENV DB_HOST=db
ENV DB_NAME=devdb
ENV DB_USER=devuser
ENV DB_PASS=changeme
ENV STATIC_DIR=/vol/web
ENV LOG_DIR=/var/log
ENV LOG_FILENAME=school_backend.log
ENV MEDIA_DIR=/vol/web/media

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

COPY ./scripts /scripts
COPY backend /app

# install  dependencies.
ARG DEV=true
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev gcc linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true"]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
    mkdir -p ${STATIC_DIR} && \
    mkdir -p ${MEDIA_DIR} && \
    mkdir -p ${LOG_DIR} && \
    touch ${LOG_DIR}/${LOG_FILENAME} && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x ${LOG_DIR} && \
    chown -R django-user:django-user ${LOG_DIR}/${LOG_FILENAME} && \
    chmod -R 755 ${STATIC_DIR} && \
    chmod -R +x ${STATIC_DIR} && \
    chown -R django-user:django-user ${STATIC_DIR} && \
    chmod -R 755 ${MEDIA_DIR} && \
    chmod -R +x ${MEDIA_DIR} && \
    chown -R django-user:django-user ${MEDIA_DIR} && \
    chmod -R +x /scripts


WORKDIR /app

EXPOSE 8000
ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

# RUN python manage.py collectstatic --noinput

CMD ["run.sh"]
