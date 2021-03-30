# pull official base image
FROM node:14 as dev

# set working directory
WORKDIR /app
EXPOSE 3000

# copy generated app
COPY . ./

# start app
CMD ["npm", "start"]
