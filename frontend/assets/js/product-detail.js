document.addEventListener("DOMContentLoaded", function () {
  loadProductDetail();
});

async function loadProductDetail() {
  var id = window.PetShop.ui.getQueryParam("id");
  var target = document.getElementById("product-detail");
  if (!id) {
    target.innerHTML = window.PetShop.ui.emptyState("Thiếu mã sản phẩm");
    return;
  }

  try {
    var product = await window.PetShop.api.request("/products/" + id, { auth: false });
    target.innerHTML =
      '<div class="product-detail">' +
      '<div class="gallery"><div class="product-image gallery-main">' + window.PetShop.ui.escapeHtml(product.name) + '</div><div class="gallery-grid">' +
      (product.images.length
        ? product.images.map(function (image) {
            return '<div class="product-image">' + window.PetShop.ui.escapeHtml(image.alt_text || product.name) + "</div>";
          }).join("")
        : '<div class="product-image">Không có ảnh</div>') +
      '</div></div><div class="summary-card">' +
      "<h1>" + window.PetShop.ui.escapeHtml(product.name) + "</h1>" +
      "<p>" + window.PetShop.ui.escapeHtml(product.description || "Sản phẩm cho thú cưng") + "</p>" +
      '<div class="summary-list">' +
      summaryRow("Danh mục", product.category) +
      summaryRow("Thương hiệu", product.brand || "--") +
      summaryRow("Loại thú cưng", product.pet_type) +
      summaryRow("Tồn kho", String(product.stock_quantity)) +
      summaryRow("Giá", window.PetShop.ui.formatCurrency(product.price)) +
      "</div>" +
      '<form id="add-to-cart-form" class="inline-fields" style="margin-top:18px">' +
      '<div class="field" style="min-width:120px"><label>Số lượng</label><input id="detail-quantity" type="number" min="1" value="1" required></div>' +
      '<div style="padding-top:30px"><button class="button" type="submit">Thêm vào giỏ</button></div>' +
      "</form></div></div>";

    document.getElementById("add-to-cart-form").addEventListener("submit", async function (event) {
      event.preventDefault();
      if (!window.PetShop.requireAuth()) {
        return;
      }
      try {
        await window.PetShop.api.request("/cart/items", {
          method: "POST",
          body: {
            product_id: Number(id),
            quantity: Number(document.getElementById("detail-quantity").value),
          },
        });
        window.PetShop.ui.toast("Đã thêm vào giỏ hàng");
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      }
    });
  } catch (error) {
    target.innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}

function summaryRow(label, value) {
  return '<div class="summary-item"><span class="muted">' + window.PetShop.ui.escapeHtml(label) + '</span><strong>' + window.PetShop.ui.escapeHtml(value) + "</strong></div>";
}
