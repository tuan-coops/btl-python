document.addEventListener("DOMContentLoaded", function () {
  var existingUser = window.PetShop.storage.getUser();
  if (existingUser && existingUser.role && existingUser.role.name === "admin") {
    window.location.href = "admin-dashboard.html";
    return;
  }

  document.getElementById("admin-login-form").addEventListener("submit", onAdminLogin);
});

async function onAdminLogin(event) {
  event.preventDefault();
  var form = event.currentTarget;
  var button = form.querySelector('button[type="submit"]');
  if (!window.PetShop.ui.prepareFormSubmit(form, button, [
    { id: "admin-login-email", label: "Email admin", required: true, type: "email" },
    { id: "admin-login-password", label: "Mat khau", required: true, minLength: 8 },
  ])) {
    return;
  }

  try {
    var result = await window.PetShop.auth.login({
      email: document.getElementById("admin-login-email").value,
      password: document.getElementById("admin-login-password").value,
    });

    if (!result.user || !result.user.role || result.user.role.name !== "admin") {
      window.PetShop.auth.logout();
      window.PetShop.ui.toast("Tài khoản này không có quyền admin", "error");
      return;
    }

    window.PetShop.ui.toast("Đăng nhập admin thành công");
    window.location.href = "admin-dashboard.html";
  } catch (error) {
    window.PetShop.ui.toast(error.message, "error");
  } finally {
    window.PetShop.ui.finishFormSubmit(button);
  }
}
