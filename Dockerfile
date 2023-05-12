FROM node:13-alpine
WORKDIR /app/frontend/

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

EXPOSE 3000
