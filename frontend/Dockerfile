FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Using dev server for now as requested (upload usually implies running state, development is implied by context pair programming)
CMD ["npm", "run", "dev", "--", "--host"]
