FROM node:22-alpine
WORKDIR /srv
COPY . .
EXPOSE 4173
CMD ["node", "server.mjs"]
