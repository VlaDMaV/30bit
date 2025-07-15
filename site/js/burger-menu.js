document.addEventListener("DOMContentLoaded", function () {
  const burgerButton = document.querySelector(".burger-button");
  const burgerModal = document.getElementById("burger-modal");
  const closeBtn = document.querySelector(".burger-modal__close");
  const navLinks = burgerModal.querySelectorAll(
    '.burger-modal__nav a[href^="#"]'
  );

  // Открытие
  burgerButton.addEventListener("click", function (e) {
    e.stopPropagation();
    // Показываем и анимируем
    burgerModal.style.display = "flex";
    // Даем браузеру применить display, чтобы transition сработал
    setTimeout(() => {
      burgerModal.classList.add("open");
      burgerModal.classList.remove("closing");
    }, 10);
  });

  // Плавное закрытие
  function closeBurgerModal() {
    burgerModal.classList.remove("open");
    burgerModal.classList.add("closing");
  }

  closeBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    closeBurgerModal();
  });

  // Закрытие по клику вне меню
  document.addEventListener("click", function (e) {
    if (
      burgerModal.classList.contains("open") &&
      !burgerModal.contains(e.target) &&
      e.target !== burgerButton
    ) {
      closeBurgerModal();
    }
  });

  // Закрытие по клику на ссылку
  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const href = link.getAttribute("href");
      if (href && href.startsWith("#")) {
        e.preventDefault();
        closeBurgerModal();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  });
});
