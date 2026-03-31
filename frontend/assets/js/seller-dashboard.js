document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureSellerAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    loadDashboard();
  });
});

async function loadDashboard() {
  var target = document.getElementById("dashboard-stats");
  try {
    var data = await window.PetShop.api.request("/seller/dashboard");
    target.innerHTML =
      '<div class="summary-grid">' +
      statCard("Tổng user", data.total_users) +
      statCard("Tổng sản phẩm", data.total_products) +
      statCard("Tổng đơn hàng", data.total_orders) +
      statCard("Đơn chờ xử lý", data.pending_orders) +
      statCard("Sản phẩm sắp hết", data.low_stock_products) +
      statCard("Doanh thu tháng", window.PetShop.ui.formatCurrency(data.monthly_revenue)) +
      "</div>";
  } catch (error) {
    target.innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}

function statCard(label, value) {
  return '<div class="mini-stat"><span class="muted">' + label + "</span><strong>" + value + "</strong></div>";
}
