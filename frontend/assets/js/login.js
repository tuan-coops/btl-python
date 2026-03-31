document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("login-form").addEventListener("submit", onLogin);
});

async function onLogin(event) {
  event.preventDefault();
  var form = event.currentTarget;
  var button = form.querySelector('button[type="submit"]');
  if (!window.PetShop.ui.prepareFormSubmit(form, button, [
    { id: "login-email", label: "Email", required: true, type: "email" },
    { id: "login-password", label: "Mat khau", required: true, minLength: 8 },
  ])) {
    return;
  }
  try {
    var result = await window.PetShop.auth.login({
      email: document.getElementById("login-email").value,
      password: document.getElementById("login-password").value,
    });
    window.PetShop.ui.toast("Đăng nhập thành công");
    if (result.user.role.name === "admin") {
      window.location.href = "admin-dashboard.html";
      return;
    }
    window.location.href = "profile.html";
  } catch (error) {
    window.PetShop.ui.toast(error.message, "error");
  } finally {
    window.PetShop.ui.finishFormSubmit(button);
  }
}
