# Rebuff는 Next.js 기반 (Node.js)
FROM node:18

WORKDIR /app

COPY . .

RUN npm install
RUN npm run build

EXPOSE 8080
CMD ["npm", "run", "start"]
