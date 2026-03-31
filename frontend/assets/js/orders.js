var ordersState = {
  page: 1,
  pageSize: 10,
};

document.addEventListener("DOMContentLoaded", function () {
  if (!window.PetShop.requireAuth()) {
    return;
  }
  loadOrders();
});

async function loadOrders() {
  var list = document.getElementById("orders-list");
  var detail = document.getElementById("order-detail");
  var pagination = document.getElementById("orders-pagination");
  list.innerHTML = "<div class=\"empty-state\">Đang tải đơn hàng...</div>";

  try {
    var data = await window.PetShop.api.request("/orders?page=" + ordersState.page + "&page_size=" + ordersState.pageSize);
    if (!data.items.length) {
      list.innerHTML = window.PetShop.ui.emptyState("Bạn chưa có đơn hàng nào");
      detail.innerHTML = "";
    } else {
      list.innerHTML = data.items.map(function (order) {
        return (
          '<article class="order-card">' +
          '<div class="action-row" style="justify-content:space-between">' +
          "<div><strong>" + window.PetShop.ui.escapeHtml(order.order_code) + "</strong><p class=\"muted\">" + window.PetShop.ui.formatDateTime(order.created_at) + "</p></div>" +
          window.PetShop.ui.renderStatus(order.status) +
          "</div>" +
          "<p>Tổng thanh toán: <strong>" + window.PetShop.ui.formatCurrency(order.total_amount) + "</strong></p>" +
          '<button class="button-ghost order-detail-button" data-id="' + order.id + '">Xem chi tiết</button>' +
          "</article>"
        );
      }).join("");

      bindOrderButtons();
      var focusId = window.PetShop.ui.getQueryParam("focus");
      if (focusId) {
        loadOrderDetail(focusId);
      } else {
        loadOrderDetail(data.items[0].id);
      }
    }

    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      ordersState.page = page;
      loadOrders();
    });
  } catch (error) {
    list.innerHTML = window.PetShop.ui.emptyState(error.message);
    detail.innerHTML = "";
  }
}

function bindOrderButtons() {
  Array.from(document.querySelectorAll(".order-detail-button")).forEach(function (button) {
    button.addEventListener("click", function () {
      loadOrderDetail(button.dataset.id);
    });
  });
}

async function loadOrderDetail(id) {
  var target = document.getElementById("order-detail");
  try {
    var order = await window.PetShop.api.request("/orders/" + id);
    target.innerHTML =
      '<div class="summary-card">' +
      "<h2>Chi tiết " + window.PetShop.ui.escapeHtml(order.order_code) + "</h2>" +
      '<div class="summary-list">' +
      summaryOrderLine("Trạng thái", order.status) +
      summaryOrderLine("Thanh toán", order.payment_method) +
      summaryOrderLine("Tạm tính", window.PetShop.ui.formatCurrency(order.subtotal)) +
      summaryOrderLine("Phí ship", window.PetShop.ui.formatCurrency(order.shipping_fee)) +
      summaryOrderLine("Tổng cộng", window.PetShop.ui.formatCurrency(order.total_amount)) +
      "</div>" +
      "<h3>Sản phẩm</h3>" +
      order.items.map(function (item) {
        return '<div class="summary-item"><span>' + window.PetShop.ui.escapeHtml(item.product_name) + " x " + item.quantity + "</span><strong>" + window.PetShop.ui.formatCurrency(item.line_total) + "</strong></div>";
      }).join("") +
      "<h3>Địa chỉ giao hàng</h3>" +
      "<p>" + window.PetShop.ui.escapeHtml(order.shipping_address.recipient_name) + " - " + window.PetShop.ui.escapeHtml(order.shipping_address.phone) + "</p>" +
      "<p>" + window.PetShop.ui.escapeHtml(order.shipping_address.line1) + ", " + window.PetShop.ui.escapeHtml(order.shipping_address.district || "") + ", " + window.PetShop.ui.escapeHtml(order.shipping_address.city || "") + ", " + window.PetShop.ui.escapeHtml(order.shipping_address.province) + "</p>" +
      "</div>";
  } catch (error) {
    target.innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}

function summaryOrderLine(label, value) {
  return '<div class="summary-item"><span class="muted">' + label + "</span><strong>" + window.PetShop.ui.escapeHtml(String(value)) + "</strong></div>";
}
