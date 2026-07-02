# ---- build stage ----
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json ./
COPY yarn.lock* ./
RUN yarn install --network-timeout 600000

COPY . .

# Same-origin in production: frontend nginx proxies /api to the backend.
ARG REACT_APP_BACKEND_URL=""
RUN printf "REACT_APP_BACKEND_URL=%s\n" "$REACT_APP_BACKEND_URL" > .env \
    && yarn build

# ---- serve stage ----
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
