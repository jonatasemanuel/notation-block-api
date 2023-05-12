FROM python:3.9-alpine3.13

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY .  /app/backend/
WORKDIR /app/backend
# EXPOSE 8000

# Build psycopg2-binary from source -- add required required dependencies
RUN apk add --virtual .build-deps --no-cache postgresql-dev gcc python3-dev musl-dev && \
        pip install --no-cache-dir -r requirements.txt && \
        apk --purge del .build-deps

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
