var adminOrdersState = { page: 1, pageSize: 10 };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureAdminAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    document.getElementById("admin-order-filter-form").addEventListener("submit", function (event) {
      event.preventDefault();
      adminOrdersState.page = 1;
      loadAdminOrders();
    });
    loadAdminOrders();
  });
});

async function loadAdminOrders() {
  var tbody = document.getElementById("admin-orders-body");
  var pagination = document.getElementById("admin-orders-pagination");
  var status = document.getElementById("admin-order-filter-status").value;
  var params = new URLSearchParams({
    page: adminOrdersState.page,
    page_size: adminOrdersState.pageSize,
  });
  if (status) {
    params.set("status", status);
  }

  try {
    var data = await window.PetShop.api.request("/admin/orders?" + params.toString());
    tbody.innerHTML = data.items.map(function (item) {
      return (
        "<tr>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.order_code) + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.user.full_name) + "</td>" +
        "<td>" + window.PetShop.ui.renderStatus(item.status) + "</td>" +
        "<td>" + window.PetShop.ui.formatCurrency(item.total_amount) + "</td>" +
        "<td>" + window.PetShop.ui.formatDateTime(item.created_at) + "</td>" +
          '<td><button class="button-ghost admin-order-detail" data-id="' + item.id + '">Xem</button></td>' +
        "</tr>"
      );
    }).join("");

    bindAdminOrderButtons(data.items);
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      adminOrdersState.page = page;
      loadAdminOrders();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="6">' + error.message + "</td></tr>";
  }
}

function bindAdminOrderButtons(items) {
  Array.from(document.querySelectorAll(".admin-order-detail")).forEach(function (button) {
    button.addEventListener("click", function () {
      var item = items.find(function (order) { return order.id === Number(button.dataset.id); });
      renderAdminOrderDetail(item);
    });
  });
}

function renderAdminOrderDetail(orderSummary) {
  window.PetShop.api.request("/admin/orders/" + orderSummary.id).then(function (order) {
    document.getElementById("admin-order-detail").innerHTML =
      '<div class="summary-card">' +
      "<h2>Đơn " + window.PetShop.ui.escapeHtml(order.order_code) + "</h2>" +
      '<div class="summary-list">' +
      '<div class="summary-item"><span class="muted">Khách hàng</span><strong>' + window.PetShop.ui.escapeHtml(order.user.full_name) + "</strong></div>" +
      '<div class="summary-item"><span class="muted">Email</span><strong>' + window.PetShop.ui.escapeHtml(order.user.email) + "</strong></div>" +
      '<div class="summary-item"><span class="muted">Tổng tiền</span><strong>' + window.PetShop.ui.formatCurrency(order.total_amount) + "</strong></div>" +
      "</div>" +
      '<div class="field"><label>Cập nhật trạng thái</label><select id="admin-order-status-select">' +
      ["pending", "confirmed", "shipping", "completed", "cancelled"].map(function (status) {
        return '<option value="' + status + '"' + (status === order.status ? " selected" : "") + ">" + status + "</option>";
      }).join("") +
      '</select></div><button class="button" id="admin-order-status-save">Lưu trạng thái</button>' +
      "<h3>Sản phẩm</h3>" +
      order.items.map(function (item) {
        return '<div class="summary-item"><span>' + window.PetShop.ui.escapeHtml(item.product_name) + " x " + item.quantity + "</span><strong>" + window.PetShop.ui.formatCurrency(item.line_total) + "</strong></div>";
      }).join("") +
      "</div>";

    document.getElementById("admin-order-status-save").addEventListener("click", async function () {
      var button = document.getElementById("admin-order-status-save");
      try {
        window.PetShop.ui.setButtonLoading(button, true, "Đang lưu...");
        await window.PetShop.api.request("/admin/orders/" + order.id + "/status", {
          method: "PATCH",
          body: { status: document.getElementById("admin-order-status-select").value },
        });
        window.PetShop.ui.toast("Đã cập nhật trạng thái đơn hàng");
        loadAdminOrders();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      } finally {
        window.PetShop.ui.setButtonLoading(button, false);
      }
    });
  }).catch(function (error) {
    document.getElementById("admin-order-detail").innerHTML = window.PetShop.ui.emptyState(error.message);
  });
}
