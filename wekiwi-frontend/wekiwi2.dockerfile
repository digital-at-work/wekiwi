FROM node:22-alpine AS build_stage
WORKDIR /app
ARG NODE_ENV
ENV NODE_ENV=$NODE_ENV
RUN echo "NODE_ENV in build_stage is set to: $NODE_ENV"
COPY package*.json .
RUN npm ci --production=false
COPY . .
RUN npm run build
RUN npm prune --production

FROM node:22-alpine AS runtime_stage
WORKDIR /app
ARG NODE_ENV
ENV NODE_ENV=$NODE_ENV
RUN echo "NODE_ENV in runtime_stage is set to: $NODE_ENV"
COPY --from=build_stage /app/build build/
COPY --from=build_stage /app/node_modules node_modules/
COPY package.json .

EXPOSE 3000

CMD ["node", "-r", "dotenv/config", "build"]
