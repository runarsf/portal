FROM node

WORKDIR /startpage

COPY ./ /startpage
RUN npm install

CMD ["npm", "start"]
