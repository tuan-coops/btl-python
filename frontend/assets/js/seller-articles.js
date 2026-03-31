var sellerArticlesState = { page: 1, pageSize: 10 };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureSellerAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    bindSellerArticleForm();
    loadSellerArticles();
  });
});

function bindSellerArticleForm() {
  document.getElementById("seller-article-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var form = event.currentTarget;
    var button = form.querySelector('button[type="submit"]');
    if (!window.PetShop.ui.prepareFormSubmit(form, button, [
      { id: "seller-article-title", label: "Tiêu đề", required: true },
      { id: "seller-article-slug", label: "Slug", required: true },
      { id: "seller-article-content", label: "Nội dung", required: true, minLength: 10 },
    ])) {
      return;
    }
    var id = document.getElementById("seller-article-id").value;
    var payload = {
      title: document.getElementById("seller-article-title").value,
      slug: document.getElementById("seller-article-slug").value,
      summary: document.getElementById("seller-article-summary").value || null,
      content: document.getElementById("seller-article-content").value,
      is_published: document.getElementById("seller-article-published").checked,
    };

    try {
      await window.PetShop.api.request("/seller/articles" + (id ? "/" + id : ""), {
        method: id ? "PATCH" : "POST",
        body: payload,
      });
      window.PetShop.ui.toast(id ? "Đã cập nhật bài viết" : "Đã tạo bài viết");
      event.target.reset();
      document.getElementById("seller-article-id").value = "";
      loadSellerArticles();
    } catch (error) {
      window.PetShop.ui.toast(error.message, "error");
    } finally {
      window.PetShop.ui.finishFormSubmit(button);
    }
  });
}

async function loadSellerArticles() {
  var tbody = document.getElementById("seller-articles-body");
  var pagination = document.getElementById("seller-articles-pagination");
  try {
    var data = await window.PetShop.api.request("/seller/articles?page=" + sellerArticlesState.page + "&page_size=" + sellerArticlesState.pageSize);
    tbody.innerHTML = data.items.map(function (item) {
      return (
        "<tr>" +
        "<td>" + item.id + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.title) + "</td>" +
        "<td>" + window.PetShop.ui.escapeHtml(item.slug) + "</td>" +
        "<td>" + (item.is_published ? "Đã publish" : "Bản nháp") + "</td>" +
        '<td class="table-actions"><button class="button-ghost edit-article" data-id="' + item.id + '">Sửa</button><button class="button-danger delete-article" data-id="' + item.id + '">Xóa</button></td>' +
        "</tr>"
      );
    }).join("");
    bindSellerArticleTable(data.items);
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      sellerArticlesState.page = page;
      loadSellerArticles();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="5">' + error.message + "</td></tr>";
  }
}

function bindSellerArticleTable(items) {
  Array.from(document.querySelectorAll(".edit-article")).forEach(function (button) {
    button.addEventListener("click", function () {
      var item = items.find(function (article) { return article.id === Number(button.dataset.id); });
      document.getElementById("seller-article-id").value = item.id;
      document.getElementById("seller-article-title").value = item.title;
      document.getElementById("seller-article-slug").value = item.slug;
      document.getElementById("seller-article-summary").value = item.summary || "";
      document.getElementById("seller-article-content").value = item.content;
      document.getElementById("seller-article-published").checked = item.is_published;
    });
  });

  Array.from(document.querySelectorAll(".delete-article")).forEach(function (button) {
    button.addEventListener("click", async function () {
      try {
        await window.PetShop.api.request("/seller/articles/" + button.dataset.id, { method: "DELETE" });
        window.PetShop.ui.toast("Đã xóa bài viết");
        loadSellerArticles();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      }
    });
  });
}
