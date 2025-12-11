# Utilise la dernière version LTS officielle de Node.js
FROM node:24.11.0

# Installe Yarn globalement
RUN corepack enable && corepack prepare yarn@stable --activate

RUN mkdir /home/node/src
WORKDIR /home/node/src
RUN chown node:node /home/node/src

RUN npm install -g @nestjs/cli
RUN npm install -g create-react-app
RUN npm install -g create-next-app

# Passe à l'utilisateur non-root
USER node

