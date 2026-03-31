var sellerProductState = { page: 1, pageSize: 10, categories: [] };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureSellerAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    bindSellerProductForm();
    loadSellerProductCategories();
    loadSellerProducts();
  });
});

async function loadSellerProductCategories() {
  try {
    var data = await window.PetShop.api.request("/seller/categories?page=1&page_size=100");
    sellerProductState.categories = data.items;
    var selects = [document.getElementById("seller-product-category"), document.getElementById("seller-product-filter-category")];
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

function bindSellerProductForm() {
  document.getElementById("seller-product-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var form = event.currentTarget;
    var button = form.querySelector('button[type="submit"]');
    if (!window.PetShop.ui.prepareFormSubmit(form, button, [
      { id: "seller-product-name", label: "Tên", required: true },
      { id: "seller-product-slug", label: "Slug", required: true },
      { id: "seller-product-sku", label: "SKU", required: true },
      { id: "seller-product-price", label: "Giá", required: true, min: 0 },
      { id: "seller-product-stock", label: "Tồn kho", required: true, min: 0 },
    ])) {
      return;
    }
    var id = document.getElementById("seller-product-id").value;
    var payload = {
      name: document.getElementById("seller-product-name").value,
      slug: document.getElementById("seller-product-slug").value,
      sku: document.getElementById("seller-product-sku").value,
      description: document.getElementById("seller-product-description").value || null,
      price: Number(document.getElementById("seller-product-price").value),
      stock_quantity: Number(document.getElementById("seller-product-stock").value),
      brand: document.getElementById("seller-product-brand").value || null,
      pet_type: document.getElementById("seller-product-pet-type").value,
      category_id: Number(document.getElementById("seller-product-category").value),
      is_active: document.getElementById("seller-product-active").checked,
      primary_image_url: document.getElementById("seller-product-image").value || null,
    };
    try {
      await window.PetShop.api.request("/seller/products" + (id ? "/" + id : ""), {
        method: id ? "PATCH" : "POST",
        body: payload,
      });
      window.PetShop.ui.toast(id ? "Đã cập nhật sản phẩm" : "Đã tạo sản phẩm");
      event.target.reset();
      document.getElementById("seller-product-id").value = "";
      loadSellerProducts();
    } catch (error) {
      window.PetShop.ui.toast(error.message, "error");
    } finally {
      window.PetShop.ui.finishFormSubmit(button);
    }
  });

  document.getElementById("seller-product-filter-form").addEventListener("submit", function (event) {
    event.preventDefault();
    sellerProductState.page = 1;
    loadSellerProducts();
  });
}

async function loadSellerProducts() {
  var tbody = document.getElementById("seller-products-body");
  var pagination = document.getElementById("seller-products-pagination");
  var params = new URLSearchParams({
    page: sellerProductState.page,
    page_size: sellerProductState.pageSize,
  });
  [
    ["category_id", document.getElementById("seller-product-filter-category").value],
    ["pet_type", document.getElementById("seller-product-filter-pet-type").value],
    ["brand", document.getElementById("seller-product-filter-brand").value],
    ["is_active", document.getElementById("seller-product-filter-active").value],
  ].forEach(function (entry) {
    if (entry[1]) {
      params.set(entry[0], entry[1]);
    }
  });

  try {
    var data = await window.PetShop.api.request("/seller/products?" + params.toString());
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

    bindSellerProductTable(data.items);
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      sellerProductState.page = page;
      loadSellerProducts();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="7">' + error.message + "</td></tr>";
  }
}

function bindSellerProductTable(items) {
  Array.from(document.querySelectorAll(".edit-product")).forEach(function (button) {
    button.addEventListener("click", function () {
      var item = items.find(function (product) { return product.id === Number(button.dataset.id); });
      document.getElementById("seller-product-id").value = item.id;
      document.getElementById("seller-product-name").value = item.name;
      document.getElementById("seller-product-slug").value = item.slug;
      document.getElementById("seller-product-sku").value = item.sku;
      document.getElementById("seller-product-description").value = item.description || "";
      document.getElementById("seller-product-price").value = item.price;
      document.getElementById("seller-product-stock").value = item.stock_quantity;
      document.getElementById("seller-product-brand").value = item.brand || "";
      document.getElementById("seller-product-pet-type").value = item.pet_type;
      document.getElementById("seller-product-category").value = item.category_id;
      document.getElementById("seller-product-active").checked = item.is_active;
      document.getElementById("seller-product-image").value = item.images.length ? item.images[0].image_url : "";
    });
  });

  Array.from(document.querySelectorAll(".delete-product")).forEach(function (button) {
    button.addEventListener("click", async function () {
      try {
        await window.PetShop.api.request("/seller/products/" + button.dataset.id, { method: "DELETE" });
        window.PetShop.ui.toast("Đã cập nhật trạng thái sản phẩm");
        loadSellerProducts();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      }
    });
  });
}
