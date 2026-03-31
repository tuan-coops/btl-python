document.addEventListener("DOMContentLoaded", function () {
  loadCategoriesPage();
});

async function loadCategoriesPage() {
  var target = document.getElementById("categories-list");
  target.innerHTML = window.PetShop.ui.emptyState("Đang tải danh mục...");

  try {
    var categories = await window.PetShop.api.request("/categories", { auth: false });
    if (!categories.length) {
      target.innerHTML = window.PetShop.ui.emptyState("Chưa có danh mục nào");
      return;
    }

    target.innerHTML = categories.map(function (item) {
      return (
        '<article class="card">' +
        '<div class="card-body">' +
        "<h3>" + window.PetShop.ui.escapeHtml(item.name) + "</h3>" +
      "<p>" + window.PetShop.ui.escapeHtml(item.description || "Danh mục sản phẩm cho thú cưng") + "</p>" +
        '<div class="action-row">' +
        '<a class="button" href="products.html?category_id=' + item.id + '">Xem sản phẩm</a>' +
        "</div></div></article>"
      );
    }).join("");
  } catch (error) {
    target.innerHTML = window.PetShop.ui.emptyState(error.message);
  }
}
