document.addEventListener("DOMContentLoaded", function () {
  var existingUser = window.PetShop.storage.getUser();
  if (existingUser && existingUser.role && existingUser.role.name === "seller") {
    window.location.href = "seller-dashboard.html";
    return;
  }

  document.getElementById("seller-login-form").addEventListener("submit", onSellerLogin);
});

async function onSellerLogin(event) {
  event.preventDefault();
  var form = event.currentTarget;
  var button = form.querySelector('button[type="submit"]');
  if (!window.PetShop.ui.prepareFormSubmit(form, button, [
    { id: "seller-login-email", label: "Email người bán", required: true, type: "email" },
    { id: "seller-login-password", label: "Mật khẩu", required: true, minLength: 8 },
  ])) {
    return;
  }

  try {
    var result = await window.PetShop.auth.login({
      email: document.getElementById("seller-login-email").value,
      password: document.getElementById("seller-login-password").value,
    });

    if (!result.user || !result.user.role || result.user.role.name !== "seller") {
      window.PetShop.auth.logout();
      window.PetShop.ui.toast("Tài khoản này không có quyền người bán", "error");
      return;
    }

    window.PetShop.ui.toast("Đăng nhập người bán thành công");
    window.location.href = "seller-dashboard.html";
  } catch (error) {
    window.PetShop.ui.toast(error.message, "error");
  } finally {
    window.PetShop.ui.finishFormSubmit(button);
  }
}
