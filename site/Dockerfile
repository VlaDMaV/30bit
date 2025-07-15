# Используем официальный образ nginx как базовый
FROM nginx:alpine

# Копируем содержимое текущей папки (ваш сайт) в папку для сервера nginx
COPY . /usr/share/nginx/html

# Порт, который будет слушать nginx
EXPOSE 80

# Запускаем nginx в фореграунд режиме (по умолчанию)
CMD ["nginx", "-g", "daemon off;"]