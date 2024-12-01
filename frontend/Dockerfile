FROM node:18-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

RUN npm install -g vite

COPY --from=build /app/dist /app/dist

EXPOSE 5173

CMD ["vite", "preview", "--port", "5173", "--host"]
