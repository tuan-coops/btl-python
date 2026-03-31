document.addEventListener("DOMContentLoaded", function () {
  if (!window.PetShop.requireAuth()) {
    return;
  }
  loadProfile();
});

async function loadProfile() {
  var target = document.getElementById("profile-content");
  try {
    var user = await window.PetShop.auth.fetchCurrentUser();
    target.innerHTML =
      '<div class="grid-two">' +
      '<section class="summary-card">' +
      "<h2>Thông tin cá nhân</h2>" +
      profileLine("Họ tên", user.full_name) +
      profileLine("Email", user.email) +
      profileLine("Số điện thoại", user.phone || "--") +
      profileLine("Vai trò", user.role.name) +
      profileLine("Trạng thái", user.is_active ? "Đang hoạt động" : "Tạm khóa") +
      "</section>" +
      '<section class="summary-card">' +
      "<h2>Điều hướng nhanh</h2>" +
      '<div class="action-row"><a class="button" href="orders.html">Xem đơn hàng</a><a class="button-ghost" href="cart.html">Xem giỏ hàng</a></div>' +
      "</section></div>";
  } catch (error) {
    target.innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}

function profileLine(label, value) {
  return '<div class="summary-item"><span class="muted">' + label + "</span><strong>" + window.PetShop.ui.escapeHtml(value) + "</strong></div>";
}
