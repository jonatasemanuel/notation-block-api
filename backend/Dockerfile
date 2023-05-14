FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt .
#RUN pip installl -r requirements.txt
RUN python -m venv /py && \
     /py/bin/pip install --upgrade pip && \
     apk add --update --no-cache postgresql-client && \
     apk add --update --no-cache --virtual .tmp-build-deps \
         build-base postgresql-dev musl-dev && \
         apk add nginx dumb-init

ENV PATH="/py/bin:$PATH"

COPY . /app
WORKDIR /app

COPY ./entrypoint.sh .
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
# FROM python:3.9-alpine3.13
# LABEL maintainer="joe"

# ENV PYTHONUNBUFFERED 1

# COPY ./requirements.txt /tmp/requirements.txt
# COPY ./requirements.dev.txt /tmp/requirements.dev.txt
# COPY . ./
# WORKDIR /backend
# # EXPOSE 8000

# ARG DEV=false
# RUN python -m venv /py && \
#     /py/bin/pip install --upgrade pip && \
#     apk add --update --no-cache postgresql-client && \
#     apk add --update --no-cache --virtual .tmp-build-deps \
#         build-base postgresql-dev musl-dev && \
#         apk add nginx dumb-init && \
#     /py/bin/pip install -r /tmp/requirements.txt && \
#     if [ $DEV = "true" ]; \
#         then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
#     fi && \
#     rm -rf /tmp && \
#     apk del .tmp-build-deps # && \
#     #adduser \
#      #   --disabled-password \
#       #  --no-create-home \
#        # django-user

# # USER django-user
# ENV PATH="/py/bin:$PATH"

# CMD gunicorn -b 0.0.0.0:8000 --worker-class=gevent --worker-connections=1000 --workers=5 backend.wsgi
