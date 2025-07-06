FROM node:22-bullseye-slim

RUN apt-get update && apt-get install -y fonts-freefont-ttf chromium

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

ENV FLAG=cube{Th1nk1ng_ReAL1Y_d3eEEe3333p}

EXPOSE 1337

CMD ["npm", "start"]