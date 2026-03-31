var adminUsersState = { page: 1, pageSize: 10 };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureAdminAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    document.getElementById("admin-users-filter-form").addEventListener("submit", function (event) {
      event.preventDefault();
      adminUsersState.page = 1;
      loadAdminUsers();
    });
    loadAdminUsers();
  });
});

async function loadAdminUsers() {
  var tbody = document.getElementById("admin-users-body");
  var pagination = document.getElementById("admin-users-pagination");
  var params = new URLSearchParams({
    page: adminUsersState.page,
    page_size: adminUsersState.pageSize,
  });
  [
    ["role", document.getElementById("admin-users-filter-role").value],
    ["is_active", document.getElementById("admin-users-filter-active").value],
  ].forEach(function (entry) {
    if (entry[1]) {
      params.set(entry[0], entry[1]);
    }
  });

  try {
    var data = await window.PetShop.api.request("/admin/users?" + params.toString());
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
      adminUsersState.page = page;
      loadAdminUsers();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="6">' + error.message + "</td></tr>";
  }
}
