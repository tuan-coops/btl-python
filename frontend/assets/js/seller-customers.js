var sellerUsersState = { page: 1, pageSize: 10 };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureSellerAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    document.getElementById("seller-users-filter-form").addEventListener("submit", function (event) {
      event.preventDefault();
      sellerUsersState.page = 1;
      loadSellerUsers();
    });
    loadSellerUsers();
  });
});

async function loadSellerUsers() {
  var tbody = document.getElementById("seller-users-body");
  var pagination = document.getElementById("seller-users-pagination");
  var params = new URLSearchParams({
    page: sellerUsersState.page,
    page_size: sellerUsersState.pageSize,
  });
  [
    ["role", document.getElementById("seller-users-filter-role").value],
    ["is_active", document.getElementById("seller-users-filter-active").value],
  ].forEach(function (entry) {
    if (entry[1]) {
      params.set(entry[0], entry[1]);
    }
  });

  try {
    var data = await window.PetShop.api.request("/seller/users?" + params.toString());
    tbody.innerHTML = data.items.map(function (user) {
      return (
        "<tr>" +
        "<td>" + user.id + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(user.full_name) + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(user.email) + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(user.phone || "--") + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(user.role) + "</td>" +
        "<td>" + (user.is_active ? "Đang hoạt động" : "Tạm khóa") + "</td>" +
        "</tr>"
      );
    }).join("");

    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      sellerUsersState.page = page;
      loadSellerUsers();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="6">' + error.message + "</td></tr>";
  }
}
