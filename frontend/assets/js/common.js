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
    adminLogin: "pages/admin-login.html",
    adminDashboard: "pages/admin-dashboard.html",
    adminProducts: "pages/admin-products.html",
    adminCategories: "pages/admin-categories.html",
    adminOrders: "pages/admin-orders.html",
    adminCustomers: "pages/admin-customers.html",
    adminArticles: "pages/admin-articles.html",
  };

  function href(pageKey) {
    return window.PetShop.config.getRootPrefix() + pages[pageKey];
  }

  function buildHeader() {
    var page = document.body.dataset.page || "";
    var user = window.PetShop.storage.getUser();
    var isAdmin = user && user.role && user.role.name === "admin";
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
      (isAdmin ? navLink("adminDashboard", "Admin", page.indexOf("admin") === 0) : "") +
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

  function navLink(pageKey, label, active) {
    return '<a class="nav-link ' + (active ? "active" : "") + '" href="' + href(pageKey) + '">' + label + "</a>";
  }

  function buildFooter() {
    var footer = document.getElementById("site-footer");
    if (!footer) {
      return;
    }
    footer.className = "site-footer";
    footer.innerHTML =
      '<div class="container">' +
      "<strong>Pet Shop Demo</strong>" +
      "<p>Frontend thuần HTML, CSS, JavaScript. API mặc định: " +
      window.PetShop.ui.escapeHtml(window.PetShop.config.getApiBaseUrl()) +
      "</p></div>";
  }

  function requireAuth(options) {
    options = options || {};
    var user = window.PetShop.storage.getUser();
    if (!window.PetShop.storage.getToken()) {
      window.location.href = href("login");
      return false;
    }
    if (options.admin && (!user || !user.role || user.role.name !== "admin")) {
      window.PetShop.ui.toast("Bạn không có quyền truy cập khu vực admin", "error");
      setTimeout(function () {
        window.location.href = href("home");
      }, 500);
      return false;
    }
    return true;
  }

  async function ensureAdminAccess() {
    if (!window.PetShop.storage.getToken()) {
      window.location.href = href("adminLogin");
      return false;
    }

    try {
      var user = await window.PetShop.auth.fetchCurrentUser();
      if (!user || !user.role || user.role.name !== "admin") {
        window.PetShop.storage.clearAuth();
        window.PetShop.ui.toast("Tài khoản không có quyền admin", "error");
        setTimeout(function () {
          window.location.href = href("adminLogin");
        }, 500);
        return false;
      }
      return true;
    } catch (error) {
      window.PetShop.storage.clearAuth();
      window.PetShop.ui.toast("Phiên đăng nhập admin không hợp lệ", "error");
      setTimeout(function () {
        window.location.href = href("adminLogin");
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
  window.PetShop.ensureAdminAccess = ensureAdminAccess;
})();
