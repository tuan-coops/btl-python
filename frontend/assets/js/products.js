var productPageState = {
  page: 1,
  pageSize: 9,
};

document.addEventListener("DOMContentLoaded", function () {
  setupProductFilters();
  loadCategoryOptions();
  loadProducts();
});

function setupProductFilters() {
  var form = document.getElementById("product-filter-form");
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    productPageState.page = 1;
    loadProducts();
  });
}

async function loadCategoryOptions() {
  var select = document.getElementById("filter-category");
  try {
    var categories = await window.PetShop.api.request("/categories", { auth: false });
    categories.forEach(function (item) {
      var option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.name;
      select.appendChild(option);
    });

    var initial = window.PetShop.ui.getQueryParam("category_id");
    if (initial) {
      select.value = initial;
    }
  } catch (error) {
    window.PetShop.ui.toast(error.message, "error");
  }
}

async function loadProducts() {
  var list = document.getElementById("products-list");
  var pagination = document.getElementById("products-pagination");
  var params = new URLSearchParams();
  params.set("page", productPageState.page);
  params.set("page_size", productPageState.pageSize);

  [
    ["search", document.getElementById("filter-search").value],
    ["category_id", document.getElementById("filter-category").value || window.PetShop.ui.getQueryParam("category_id") || ""],
    ["pet_type", document.getElementById("filter-pet-type").value],
    ["brand", document.getElementById("filter-brand").value],
    ["price_min", document.getElementById("filter-price-min").value],
    ["price_max", document.getElementById("filter-price-max").value],
  ].forEach(function (item) {
    if (item[1]) {
      params.set(item[0], item[1]);
    }
  });

  list.innerHTML = "<div class=\"empty-state\">Đang tải sản phẩm...</div>";

  try {
    var data = await window.PetShop.api.request("/products?" + params.toString(), { auth: false });
    if (!data.items.length) {
      list.innerHTML = window.PetShop.ui.emptyState("Không tìm thấy sản phẩm phù hợp");
    } else {
      list.innerHTML = data.items.map(function (item) {
        return (
          '<article class="card">' +
          '<div class="product-image">' + window.PetShop.ui.escapeHtml(item.name) + "</div>" +
          '<div class="card-body">' +
          "<h3>" + window.PetShop.ui.escapeHtml(item.name) + "</h3>" +
          '<div class="chip-row"><span class="chip">' + window.PetShop.ui.escapeHtml(item.category) + '</span><span class="chip">' + window.PetShop.ui.escapeHtml(item.pet_type) + "</span></div>" +
          "<p>" + window.PetShop.ui.escapeHtml(item.brand || "Không có thương hiệu") + "</p>" +
          '<div class="action-row"><strong>' + window.PetShop.ui.formatCurrency(item.price) + '</strong><a class="button" href="product-detail.html?id=' + item.id + '">Chi tiết</a></div>' +
          "</div></article>"
        );
      }).join("");
    }
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      productPageState.page = page;
      loadProducts();
    });
  } catch (error) {
    list.innerHTML = window.PetShop.ui.emptyState(error.message);
    pagination.innerHTML = "";
  }
}
