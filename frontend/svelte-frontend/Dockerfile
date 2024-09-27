FROM node:18

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

RUN npm run build
RUN npm install -g serve
ENV HOST=0.0.0.0

EXPOSE 3000

VOLUME /app/dist
# Copy the built files to the volume
RUN mkdir -p /app/dist && cp -r public/* /app/dist

#CMD ["serve", "-s", "public"]
CMD ["npm", "run", "dev"]
