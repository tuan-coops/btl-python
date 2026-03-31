document.addEventListener("DOMContentLoaded", function () {
  if (!window.PetShop.requireAuth()) {
    return;
  }
  bindCheckoutForm();
  preloadCheckout();
});

async function preloadCheckout() {
  try {
    var results = await Promise.all([
      window.PetShop.api.request("/cart"),
      window.PetShop.auth.fetchCurrentUser(),
    ]);
    renderCheckoutCart(results[0]);
    fillUserInfo(results[1]);
  } catch (error) {
    document.getElementById("checkout-cart-summary").innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}

function renderCheckoutCart(cart) {
  var target = document.getElementById("checkout-cart-summary");
  if (!cart.items.length) {
    target.innerHTML = window.PetShop.ui.emptyState("Không thể thanh toán vì giỏ hàng trống");
    return;
  }
  target.innerHTML =
    "<h2>Đơn hàng của bạn</h2>" +
    cart.items.map(function (item) {
      return '<div class="summary-item"><span>' + window.PetShop.ui.escapeHtml(item.product_name) + " x " + item.quantity + "</span><strong>" + window.PetShop.ui.formatCurrency(item.line_total) + "</strong></div>";
    }).join("") +
    '<hr><div class="summary-item"><span class="muted">Tam tinh</span><strong>' + window.PetShop.ui.formatCurrency(cart.subtotal) + "</strong></div>";
}

function fillUserInfo(user) {
  document.getElementById("checkout-recipient").value = user.full_name || "";
  document.getElementById("checkout-phone").value = user.phone || "";
}

function bindCheckoutForm() {
  document.getElementById("checkout-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var form = event.currentTarget;
    var button = form.querySelector('button[type="submit"]');
    if (!window.PetShop.ui.prepareFormSubmit(form, button, [
      { id: "checkout-recipient", label: "Người nhận", required: true },
      { id: "checkout-phone", label: "Số điện thoại", required: true, minLength: 8 },
      { id: "checkout-line1", label: "Địa chỉ", required: true },
      { id: "checkout-district", label: "District", required: true },
      { id: "checkout-city", label: "City", required: true },
      { id: "checkout-province", label: "Province", required: true },
      { id: "checkout-country", label: "Quốc gia", required: true },
    ])) {
      return;
    }
    var payload = {
      recipient_name: document.getElementById("checkout-recipient").value,
      phone: document.getElementById("checkout-phone").value,
      line1: document.getElementById("checkout-line1").value,
      line2: document.getElementById("checkout-line2").value || null,
      ward: document.getElementById("checkout-ward").value || null,
      district: document.getElementById("checkout-district").value,
      city: document.getElementById("checkout-city").value,
      province: document.getElementById("checkout-province").value,
      country: document.getElementById("checkout-country").value,
      payment_method: document.getElementById("checkout-payment").value,
      note: document.getElementById("checkout-note").value || null,
    };

    try {
      var order = await window.PetShop.api.request("/orders/checkout", {
        method: "POST",
        body: payload,
      });
      window.PetShop.ui.toast("Đặt hàng thành công");
      window.location.href = "orders.html?focus=" + order.id;
    } catch (error) {
      window.PetShop.ui.toast(error.message, "error");
    } finally {
      window.PetShop.ui.finishFormSubmit(button);
    }
  });
}
