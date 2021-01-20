# pull official base image
FROM node:14

# set working directory
WORKDIR /app
EXPOSE 3000

# install modules
COPY package.json ./
COPY package-lock.json ./
COPY .npmrc ./

RUN npm i
RUN npm install react-scripts@3.4.1 -g --silent

# start app
CMD ["npm", "start"]