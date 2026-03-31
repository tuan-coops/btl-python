document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("register-form").addEventListener("submit", onRegister);
});

async function onRegister(event) {
  event.preventDefault();
  var form = event.currentTarget;
  var button = form.querySelector('button[type="submit"]');
  if (!window.PetShop.ui.prepareFormSubmit(form, button, [
    { id: "register-full-name", label: "Ho ten", required: true },
    { id: "register-email", label: "Email", required: true, type: "email" },
    { id: "register-password", label: "Mat khau", required: true, minLength: 8 },
  ])) {
    return;
  }
  var payload = {
    full_name: document.getElementById("register-full-name").value,
    email: document.getElementById("register-email").value,
    phone: document.getElementById("register-phone").value || null,
    password: document.getElementById("register-password").value,
  };

  try {
    await window.PetShop.auth.register(payload);
    window.PetShop.ui.toast("Đăng ký thành công, vui lòng đăng nhập");
    setTimeout(function () {
      window.location.href = "login.html";
    }, 500);
  } catch (error) {
    window.PetShop.ui.toast(error.message, "error");
  } finally {
    window.PetShop.ui.finishFormSubmit(button);
  }
}
