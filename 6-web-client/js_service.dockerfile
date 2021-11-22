# pull official base image
FROM node:14 as dev
# set working directory
WORKDIR /app
EXPOSE 3000

# install modules
COPY package.json package-lock.json ./
COPY cogment.yaml ./
COPY *.proto ./

RUN mkdir src
RUN npm i
RUN npx cogment-js-sdk-generate
RUN npm run protos

# copy generated app
COPY . ./

# start app
CMD ["npm", "start"]
