# frontend/Dockerfile
# Fazda 1: Build
FROM node:20-alpine AS build_stage

WORKDIR /app

COPY package.json yarn.lock package-lock.json ./
RUN npm install --frozen-lockfile # Użyj npm, jeśli wolisz yarn to yarn install

COPY . .

RUN npm run build

# Fazda 2: Serve (możesz użyć lekkiego serwera np. Caddy/Nginx, albo po prostu serwować statyczne pliki z Nuxt)
# Nuxt 3 generuje samodzielny serwer produkcyjny w `.output/server`
FROM node:20-alpine AS production_stage

WORKDIR /app

COPY --from=build_stage /app/.output .

EXPOSE 3000

CMD ["node", "server/index.mjs"]