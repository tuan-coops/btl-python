var adminProductState = { page: 1, pageSize: 10, categories: [] };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureAdminAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    bindAdminProductForm();
    loadAdminProductCategories();
    loadAdminProducts();
  });
});

async function loadAdminProductCategories() {
  try {
    var data = await window.PetShop.api.request("/admin/categories?page=1&page_size=100");
    adminProductState.categories = data.items;
    var selects = [document.getElementById("admin-product-category"), document.getElementById("admin-product-filter-category")];
    selects.forEach(function (select, index) {
      var first = index === 1 ? '<option value="">Tất cả danh mục</option>' : '<option value="">Chọn danh mục</option>';
      select.innerHTML = first + data.items.map(function (item) {
        return '<option value="' + item.id + '">' + window.PetShop.ui.escapeHtml(item.name) + "</option>";
      }).join("");
    });
  } catch (error) {
    window.PetShop.ui.toast(error.message, "error");
  }
}

function bindAdminProductForm() {
  document.getElementById("admin-product-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var form = event.currentTarget;
    var button = form.querySelector('button[type="submit"]');
    if (!window.PetShop.ui.prepareFormSubmit(form, button, [
      { id: "admin-product-name", label: "Tên", required: true },
      { id: "admin-product-slug", label: "Slug", required: true },
      { id: "admin-product-sku", label: "SKU", required: true },
      { id: "admin-product-price", label: "Giá", required: true, min: 0 },
      { id: "admin-product-stock", label: "Tồn kho", required: true, min: 0 },
    ])) {
      return;
    }
    var id = document.getElementById("admin-product-id").value;
    var payload = {
      name: document.getElementById("admin-product-name").value,
      slug: document.getElementById("admin-product-slug").value,
      sku: document.getElementById("admin-product-sku").value,
      description: document.getElementById("admin-product-description").value || null,
      price: Number(document.getElementById("admin-product-price").value),
      stock_quantity: Number(document.getElementById("admin-product-stock").value),
      brand: document.getElementById("admin-product-brand").value || null,
      pet_type: document.getElementById("admin-product-pet-type").value,
      category_id: Number(document.getElementById("admin-product-category").value),
      is_active: document.getElementById("admin-product-active").checked,
      primary_image_url: document.getElementById("admin-product-image").value || null,
    };
    try {
      await window.PetShop.api.request("/admin/products" + (id ? "/" + id : ""), {
        method: id ? "PATCH" : "POST",
        body: payload,
      });
      window.PetShop.ui.toast(id ? "Đã cập nhật sản phẩm" : "Đã tạo sản phẩm");
      event.target.reset();
      document.getElementById("admin-product-id").value = "";
      loadAdminProducts();
    } catch (error) {
      window.PetShop.ui.toast(error.message, "error");
    } finally {
      window.PetShop.ui.finishFormSubmit(button);
    }
  });

  document.getElementById("admin-product-filter-form").addEventListener("submit", function (event) {
    event.preventDefault();
    adminProductState.page = 1;
    loadAdminProducts();
  });
}

async function loadAdminProducts() {
  var tbody = document.getElementById("admin-products-body");
  var pagination = document.getElementById("admin-products-pagination");
  var params = new URLSearchParams({
    page: adminProductState.page,
    page_size: adminProductState.pageSize,
  });
  [
    ["category_id", document.getElementById("admin-product-filter-category").value],
    ["pet_type", document.getElementById("admin-product-filter-pet-type").value],
    ["brand", document.getElementById("admin-product-filter-brand").value],
    ["is_active", document.getElementById("admin-product-filter-active").value],
  ].forEach(function (entry) {
    if (entry[1]) {
      params.set(entry[0], entry[1]);
    }
  });

  try {
    var data = await window.PetShop.api.request("/admin/products?" + params.toString());
    tbody.innerHTML = data.items.map(function (item) {
      return (
        "<tr>" +
        "<td>" + item.id + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.name) + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.category_name) + "</td>" +
        "<td>" + window.PetShop.ui.formatCurrency(item.price) + "</td>" +
        "<td>" + item.stock_quantity + "</td>" +
        "<td>" + (item.is_active ? "Có" : "Không") + "</td>" +
        '<td class="table-actions"><button class="button-ghost edit-product" data-id="' + item.id + '">Sửa</button><button class="button-danger delete-product" data-id="' + item.id + '">Ẩn/Xóa</button></td>' +
        "</tr>"
      );
    }).join("");

    bindAdminProductTable(data.items);
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      adminProductState.page = page;
      loadAdminProducts();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="7">' + error.message + "</td></tr>";
  }
}

function bindAdminProductTable(items) {
  Array.from(document.querySelectorAll(".edit-product")).forEach(function (button) {
    button.addEventListener("click", function () {
      var item = items.find(function (product) { return product.id === Number(button.dataset.id); });
      document.getElementById("admin-product-id").value = item.id;
      document.getElementById("admin-product-name").value = item.name;
      document.getElementById("admin-product-slug").value = item.slug;
      document.getElementById("admin-product-sku").value = item.sku;
      document.getElementById("admin-product-description").value = item.description || "";
      document.getElementById("admin-product-price").value = item.price;
      document.getElementById("admin-product-stock").value = item.stock_quantity;
      document.getElementById("admin-product-brand").value = item.brand || "";
      document.getElementById("admin-product-pet-type").value = item.pet_type;
      document.getElementById("admin-product-category").value = item.category_id;
      document.getElementById("admin-product-active").checked = item.is_active;
      document.getElementById("admin-product-image").value = item.images.length ? item.images[0].image_url : "";
    });
  });

  Array.from(document.querySelectorAll(".delete-product")).forEach(function (button) {
    button.addEventListener("click", async function () {
      try {
        await window.PetShop.api.request("/admin/products/" + button.dataset.id, { method: "DELETE" });
        window.PetShop.ui.toast("Đã cập nhật trạng thái sản phẩm");
        loadAdminProducts();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      }
    });
  });
}
