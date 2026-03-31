document.addEventListener("DOMContentLoaded", function () {
  if (!window.PetShop.requireAuth()) {
    return;
  }
  loadCart();
});

async function loadCart() {
  var target = document.getElementById("cart-content");
  try {
    var cart = await window.PetShop.api.request("/cart");
    renderCart(cart, target);
  } catch (error) {
    target.innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}

function renderCart(cart, target) {
  if (!cart.items.length) {
    target.innerHTML =
      window.PetShop.ui.emptyState("Giỏ hàng đang trống") +
      '<div style="margin-top:16px"><a class="button" href="products.html">Đi mua hàng</a></div>';
    return;
  }

  target.innerHTML =
    '<div class="grid-two">' +
    '<div class="table-card">' +
    cart.items.map(function (item) {
      return (
        '<div class="cart-item">' +
        "<h3>" + window.PetShop.ui.escapeHtml(item.product_name) + "</h3>" +
        '<div class="chip-row"><span class="chip">Đơn giá: ' + window.PetShop.ui.formatCurrency(item.unit_price) + '</span><span class="chip">Thành tiền: ' + window.PetShop.ui.formatCurrency(item.line_total) + "</span></div>" +
        '<div class="action-row" style="margin-top:14px">' +
        '<input type="number" min="1" value="' + item.quantity + '" data-item-id="' + item.id + '" class="cart-qty-input" style="width:90px">' +
        '<button class="button-ghost cart-update-button" data-item-id="' + item.id + '">Cập nhật</button>' +
        '<button class="button-danger cart-delete-button" data-item-id="' + item.id + '">Xóa</button>' +
        "</div></div>"
      );
    }).join("") +
    '</div><aside class="summary-card">' +
    "<h2>Tổng kết</h2>" +
    summaryLine("Số lượng", cart.total_quantity) +
    summaryLine("Tạm tính", window.PetShop.ui.formatCurrency(cart.subtotal)) +
    '<div style="margin-top:18px"><a class="button" href="checkout.html">Tiến hành thanh toán</a></div>' +
    "</aside></div>";

  bindCartActions();
}

function summaryLine(label, value) {
  return '<div class="summary-item"><span class="muted">' + label + "</span><strong>" + value + "</strong></div>";
}

function bindCartActions() {
  Array.from(document.querySelectorAll(".cart-update-button")).forEach(function (button) {
    button.addEventListener("click", async function () {
      var input = document.querySelector('.cart-qty-input[data-item-id="' + button.dataset.itemId + '"]');
      if (Number(input.value) <= 0) {
        window.PetShop.ui.toast("Số lượng phải lớn hơn 0", "error");
        return;
      }
      try {
        window.PetShop.ui.setButtonLoading(button, true, "Đang lưu...");
        await window.PetShop.api.request("/cart/items/" + button.dataset.itemId, {
          method: "PATCH",
          body: { quantity: Number(input.value) },
        });
        window.PetShop.ui.toast("Đã cập nhật giỏ hàng");
        loadCart();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      } finally {
        window.PetShop.ui.setButtonLoading(button, false);
      }
    });
  });

  Array.from(document.querySelectorAll(".cart-delete-button")).forEach(function (button) {
    button.addEventListener("click", async function () {
      try {
        window.PetShop.ui.setButtonLoading(button, true, "Đang xóa...");
        await window.PetShop.api.request("/cart/items/" + button.dataset.itemId, { method: "DELETE" });
        window.PetShop.ui.toast("Đã xóa sản phẩm");
        loadCart();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      } finally {
        window.PetShop.ui.setButtonLoading(button, false);
      }
    });
  });
}
