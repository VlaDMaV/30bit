# Используем официальный Node.js образ (можно alpine для легкости)
FROM node:18-alpine

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json (если есть)
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install --production

# Копируем весь код приложения
COPY . .

# Открываем порт (твой сервер слушает 3000)
EXPOSE 3000

# Запускаем сервер
CMD ["node", "server.js"]