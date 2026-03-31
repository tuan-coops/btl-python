document.addEventListener("DOMContentLoaded", function () {
  loadHome();
});

async function loadHome() {
  var featured = document.getElementById("featured-products");
  var categories = document.getElementById("home-categories");
  var articles = document.getElementById("home-articles");

  try {
    var results = await Promise.all([
      window.PetShop.api.request("/products?page=1&page_size=6", { auth: false }),
      window.PetShop.api.request("/categories", { auth: false }),
      window.PetShop.api.request("/articles?page=1&page_size=3", { auth: false }),
    ]);

    renderFeaturedProducts(results[0].items || [], featured);
    renderCategories(results[1] || [], categories);
    renderArticles(results[2].items || [], articles);
  } catch (error) {
    featured.innerHTML = window.PetShop.ui.emptyState(error.message);
    categories.innerHTML = "";
    articles.innerHTML = "";
  }
}

function renderFeaturedProducts(items, target) {
  if (!items.length) {
    target.innerHTML = window.PetShop.ui.emptyState("Chưa có sản phẩm để hiển thị");
    return;
  }

  target.innerHTML = items.map(function (item) {
    return (
      '<article class="card">' +
      '<div class="product-image">' + window.PetShop.ui.escapeHtml(item.name) + "</div>" +
      '<div class="card-body">' +
      '<div class="chip-row"><span class="chip">' + window.PetShop.ui.escapeHtml(item.category) + '</span><span class="chip">' + window.PetShop.ui.escapeHtml(item.pet_type) + "</span></div>" +
      "<h3>" + window.PetShop.ui.escapeHtml(item.name) + "</h3>" +
      "<p class=\"muted\">" + window.PetShop.ui.escapeHtml(item.brand || "Thương hiệu đang cập nhật") + "</p>" +
      '<div class="action-row"><strong>' + window.PetShop.ui.formatCurrency(item.price) + '</strong><a class="button" href="' + window.PetShop.href("products").replace("products.html", "product-detail.html") + "?id=" + item.id + '">Xem chi tiết</a></div>' +
      "</div></article>"
    );
  }).join("");
}

function renderCategories(items, target) {
  target.innerHTML = items.map(function (item) {
    return (
      '<article class="stat-tile">' +
      "<strong>" + window.PetShop.ui.escapeHtml(item.name) + "</strong>" +
      "<p>" + window.PetShop.ui.escapeHtml(item.description || "Danh mục dành cho shop thú cưng") + "</p>" +
      '<a class="nav-link active" href="' + window.PetShop.href("products") + "?category_id=" + item.id + '">Xem sản phẩm</a>' +
      "</article>"
    );
  }).join("");
}

function renderArticles(items, target) {
  if (!items.length) {
    target.innerHTML = window.PetShop.ui.emptyState("Chưa có bài viết công khai");
    return;
  }

  target.innerHTML = items.map(function (item) {
    return (
      '<article class="article-card">' +
      "<h3>" + window.PetShop.ui.escapeHtml(item.title) + "</h3>" +
      "<p>" + window.PetShop.ui.escapeHtml(item.summary || "Bài viết chia sẻ kinh nghiệm chăm sóc thú cưng") + "</p>" +
      '<div class="badge">Đăng ngày ' + window.PetShop.ui.formatDateTime(item.published_at) + "</div>" +
      "</article>"
    );
  }).join("");
}
