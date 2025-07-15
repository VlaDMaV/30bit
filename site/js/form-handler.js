document.addEventListener("DOMContentLoaded", function () {
  // Инициализация SmartCaptcha
  const captchaContainer = document.getElementById("captcha-container");
  const form = document.getElementById("contactForm");
  const consentCheckbox = document.getElementById("consent");

  const openFormBtn = document.getElementById("openFormBtn");
  const formWrapper = document.getElementById("formWrapper");

  openFormBtn.addEventListener("click", function () {
    formWrapper.classList.remove("hidden");
  });

  let captchaToken = "";

  // Клиентский ключ
  const smartCaptcha = window.smartCaptcha.render(captchaContainer, {
    sitekey: "ysc1_COEPBkHblFaZwjPcEyG606QQUUqad5fOwFtavjiB24083a65",
    callback: function (token) {
      captchaToken = token;
    },
    invisible: false, // Установите true для невидимой капчи
    hl: "ru", // Язык интерфейса капчи (по умолчанию английский)
  });

  // Обработка отправки формы
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    // Получаем значения полей
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    
    // Проверка email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      alert("Пожалуйста, введите корректный email адрес");
      return;
    }

    // Проверка телефона (российский формат: +7 xxx xxx xx xx или 8 xxx xxx xx xx)
    const phoneRegex = /^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/;
    if (!phoneRegex.test(phone)) {
      alert("Пожалуйста, введите корректный номер телефона (формат: +7 xxx xxx xx xx или 8 xxx xxx xx xx)");
      return;
    }

    // Проверка капчи
    if (!captchaToken) {
      alert("Пожалуйста, подтвердите, что вы не робот");
      return;
    }

    // Проверка согласия на обработку персональных данных
    if (!consentCheckbox.checked) {
      alert(
        "Пожалуйста, подтвердите согласие на обработку персональных данных"
      );
      return;
    }

    // Сбор данных формы
    const formData = new FormData(form);
    formData.append("captchaToken", captchaToken);

    // Отправка данных на сервер
    try {
      const response = await fetch("http://localhost:3000/feedback", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        // Успешная отправка
        form.reset();
        alert("Спасибо! Ваша заявка отправлена.");

        
      } else {
        // Ошибка от сервера
        alert(
          "Произошла ошибка при отправке формы. Пожалуйста, попробуйте еще раз."
        );
      }
    } catch (error) {
      // Ошибка сети или другая ошибка
      console.error("Error:", error);
      alert(
        "Произошла ошибка при отправке формы. Пожалуйста, попробуйте еще раз."
      );
    }
  });
});
