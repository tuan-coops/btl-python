(function () {
  var pages = {
    home: "index.html",
    categories: "pages/categories.html",
    products: "pages/products.html",
    cart: "pages/cart.html",
    checkout: "pages/checkout.html",
    login: "pages/login.html",
    register: "pages/register.html",
    profile: "pages/profile.html",
    orders: "pages/orders.html",
    sellerLogin: "pages/seller-login.html",
    sellerDashboard: "pages/seller-dashboard.html",
    sellerProducts: "pages/seller-products.html",
    sellerCategories: "pages/seller-categories.html",
    sellerOrders: "pages/seller-orders.html",
    sellerCustomers: "pages/seller-customers.html",
    sellerArticles: "pages/seller-articles.html",
  };

  function href(pageKey) {
    return window.PetShop.config.getRootPrefix() + pages[pageKey];
  }

  function navLink(pageKey, label, active) {
    return '<a class="nav-link ' + (active ? "active" : "") + '" href="' + href(pageKey) + '">' + label + "</a>";
  }

  function buildHeader() {
    var page = document.body.dataset.page || "";
    var user = window.PetShop.storage.getUser();
    var isSeller = user && user.role && user.role.name === "seller";
    var header = document.getElementById("site-header");

    if (!header) {
      return;
    }

    header.className = "site-header";
    header.innerHTML =
      '<div class="container topbar">' +
      '<a class="brand" href="' + href("home") + '">' +
      '<span class="brand-badge">P</span><span>Pet Shop</span></a>' +
      '<nav class="nav-row">' +
      navLink("home", "Trang chủ", page === "home") +
      navLink("categories", "Danh mục", page === "categories") +
      navLink("products", "Sản phẩm", page === "products" || page === "product-detail") +
      navLink("cart", "Giỏ hàng", page === "cart") +
      navLink("orders", "Đơn hàng", page === "orders") +
      '</nav><div class="nav-actions">' +
      (isSeller ? navLink("sellerDashboard", "Người bán", page.indexOf("seller") === 0) : "") +
      (user
        ? '<a class="nav-link ' + (page === "profile" ? "active" : "") + '" href="' + href("profile") + '">Tài khoản</a>' +
          '<button class="button-ghost" id="logout-button">Đăng xuất</button>'
        : '<a class="nav-link ' + (page === "login" ? "active" : "") + '" href="' + href("login") + '">Đăng nhập</a>' +
          '<a class="button" href="' + href("register") + '">Đăng ký</a>') +
      "</div></div>";

    var logoutButton = document.getElementById("logout-button");
    if (logoutButton) {
      logoutButton.addEventListener("click", function () {
        window.PetShop.auth.logout();
        window.PetShop.ui.toast("Đã đăng xuất");
        setTimeout(function () {
          window.location.href = href("home");
        }, 400);
      });
    }
  }

  function buildFooter() {
    var footer = document.getElementById("site-footer");
    if (!footer) {
      return;
    }
    footer.innerHTML = "";
  }

  function requireAuth(options) {
    options = options || {};
    var user = window.PetShop.storage.getUser();
    if (!window.PetShop.storage.getToken()) {
      window.location.href = href("login");
      return false;
    }
    if (options.seller && (!user || !user.role || user.role.name !== "seller")) {
      window.PetShop.ui.toast("Bạn không có quyền truy cập khu vực người bán", "error");
      setTimeout(function () {
        window.location.href = href("home");
      }, 500);
      return false;
    }
    return true;
  }

  async function ensureSellerAccess() {
    if (!window.PetShop.storage.getToken()) {
      window.location.href = href("sellerLogin");
      return false;
    }

    try {
      var user = await window.PetShop.auth.fetchCurrentUser();
      if (!user || !user.role || user.role.name !== "seller") {
        window.PetShop.storage.clearAuth();
        window.PetShop.ui.toast("Tài khoản không có quyền người bán", "error");
        setTimeout(function () {
          window.location.href = href("sellerLogin");
        }, 500);
        return false;
      }
      return true;
    } catch (error) {
      window.PetShop.storage.clearAuth();
      window.PetShop.ui.toast("Phiên đăng nhập người bán không hợp lệ", "error");
      setTimeout(function () {
        window.location.href = href("sellerLogin");
      }, 500);
      return false;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    buildHeader();
    buildFooter();
  });

  window.PetShop = window.PetShop || {};
  window.PetShop.pages = pages;
  window.PetShop.href = href;
  window.PetShop.requireAuth = requireAuth;
  window.PetShop.ensureSellerAccess = ensureSellerAccess;
})();
