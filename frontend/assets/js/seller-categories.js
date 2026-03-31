var sellerCategoryState = { page: 1, pageSize: 10 };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureSellerAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    bindCategoryForm();
    loadSellerCategories();
  });
});

function bindCategoryForm() {
  document.getElementById("seller-category-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var form = event.currentTarget;
    var button = form.querySelector('button[type="submit"]');
    if (!window.PetShop.ui.prepareFormSubmit(form, button, [
      { id: "seller-category-name", label: "Tên danh mục", required: true },
      { id: "seller-category-slug", label: "Slug", required: true },
    ])) {
      return;
    }
    var id = document.getElementById("seller-category-id").value;
    var payload = {
      name: document.getElementById("seller-category-name").value,
      slug: document.getElementById("seller-category-slug").value,
      description: document.getElementById("seller-category-description").value || null,
      is_active: document.getElementById("seller-category-active").checked,
    };

    try {
      await window.PetShop.api.request("/seller/categories" + (id ? "/" + id : ""), {
        method: id ? "PATCH" : "POST",
        body: payload,
      });
      window.PetShop.ui.toast(id ? "Đã cập nhật danh mục" : "Đã tạo danh mục");
      event.target.reset();
      document.getElementById("seller-category-id").value = "";
      loadSellerCategories();
    } catch (error) {
      window.PetShop.ui.toast(error.message, "error");
    } finally {
      window.PetShop.ui.finishFormSubmit(button);
    }
  });
}

async function loadSellerCategories() {
  var tbody = document.getElementById("seller-categories-body");
  var pagination = document.getElementById("seller-categories-pagination");
  try {
    var data = await window.PetShop.api.request("/seller/categories?page=" + sellerCategoryState.page + "&page_size=" + sellerCategoryState.pageSize);
    tbody.innerHTML = data.items.map(function (item) {
      return (
        "<tr>" +
        "<td>" + item.id + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.name) + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.slug) + "</td>" +
        "<td>" + (item.is_active ? "Có" : "Không") + "</td>" +
        '<td class="table-actions"><button class="button-ghost edit-category" data-id="' + item.id + '">Sửa</button><button class="button-danger delete-category" data-id="' + item.id + '">Ẩn/Xóa</button></td>' +
        "</tr>"
      );
    }).join("");
    bindCategoryTable(data.items);
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      sellerCategoryState.page = page;
      loadSellerCategories();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="5">' + error.message + "</td></tr>";
  }
}

function bindCategoryTable(items) {
  Array.from(document.querySelectorAll(".edit-category")).forEach(function (button) {
    button.addEventListener("click", function () {
      var item = items.find(function (category) { return category.id === Number(button.dataset.id); });
      document.getElementById("seller-category-id").value = item.id;
      document.getElementById("seller-category-name").value = item.name;
      document.getElementById("seller-category-slug").value = item.slug;
      document.getElementById("seller-category-description").value = item.description || "";
      document.getElementById("seller-category-active").checked = item.is_active;
    });
  });

  Array.from(document.querySelectorAll(".delete-category")).forEach(function (button) {
    button.addEventListener("click", async function () {
      try {
        await window.PetShop.api.request("/seller/categories/" + button.dataset.id, { method: "DELETE" });
        window.PetShop.ui.toast("Đã cập nhật trạng thái danh mục");
        loadSellerCategories();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      }
    });
  });
}
