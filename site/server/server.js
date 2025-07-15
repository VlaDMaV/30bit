const express = require('express');
const multer = require('multer');
const cors = require('cors');

const app = express();
const port = 3000;

// Используем CORS, чтобы фронт может обращаться к серверу
app.use(cors());

// Настройка Multer для обработки FormData
const upload = multer();

app.post('/feedback', upload.none(), (req, res) => {
  const { email, phone, message, consent, captchaToken } = req.body;

  // Проверка полей
  if (!email || !phone || !message || !consent || !captchaToken) {
    return res.status(400).json({ success: false, error: 'Не все поля заполнены' });
  }

  // Здесь можно добавить проверку капчи на стороне сервера, отправив captchaToken в Яндекс или Google

  // Пример логирования полученных данных
  console.log('Новая заявка:');
  console.log('Email:', email);
  console.log('Телефон:', phone);
  console.log('Сообщение:', message);
  console.log('Согласие на обработку:', consent);
  console.log('Токен капчи:', captchaToken);

  return res.json({ success: true });
});

app.listen(port, () => {
  console.log(`Сервер запущен на http://localhost:${port}`);
});
