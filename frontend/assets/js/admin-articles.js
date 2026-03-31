var adminArticlesState = { page: 1, pageSize: 10 };

document.addEventListener("DOMContentLoaded", function () {
  window.PetShop.ensureAdminAccess().then(function (ok) {
    if (!ok) {
      return;
    }
    bindAdminArticleForm();
    loadAdminArticles();
  });
});

function bindAdminArticleForm() {
  document.getElementById("admin-article-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    var form = event.currentTarget;
    var button = form.querySelector('button[type="submit"]');
    if (!window.PetShop.ui.prepareFormSubmit(form, button, [
      { id: "admin-article-title", label: "Tiêu đề", required: true },
      { id: "admin-article-slug", label: "Slug", required: true },
      { id: "admin-article-content", label: "Nội dung", required: true, minLength: 10 },
    ])) {
      return;
    }
    var id = document.getElementById("admin-article-id").value;
    var payload = {
      title: document.getElementById("admin-article-title").value,
      slug: document.getElementById("admin-article-slug").value,
      summary: document.getElementById("admin-article-summary").value || null,
      content: document.getElementById("admin-article-content").value,
      is_published: document.getElementById("admin-article-published").checked,
    };

    try {
      await window.PetShop.api.request("/admin/articles" + (id ? "/" + id : ""), {
        method: id ? "PATCH" : "POST",
        body: payload,
      });
      window.PetShop.ui.toast(id ? "Đã cập nhật bài viết" : "Đã tạo bài viết");
      event.target.reset();
      document.getElementById("admin-article-id").value = "";
      loadAdminArticles();
    } catch (error) {
      window.PetShop.ui.toast(error.message, "error");
    } finally {
      window.PetShop.ui.finishFormSubmit(button);
    }
  });
}

async function loadAdminArticles() {
  var tbody = document.getElementById("admin-articles-body");
  var pagination = document.getElementById("admin-articles-pagination");
  try {
    var data = await window.PetShop.api.request("/admin/articles?page=" + adminArticlesState.page + "&page_size=" + adminArticlesState.pageSize);
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
    bindAdminArticleTable(data.items);
    window.PetShop.ui.renderPagination(pagination, data, function (page) {
      adminArticlesState.page = page;
      loadAdminArticles();
    });
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="5">' + error.message + "</td></tr>";
  }
}

function bindAdminArticleTable(items) {
  Array.from(document.querySelectorAll(".edit-article")).forEach(function (button) {
    button.addEventListener("click", function () {
      var item = items.find(function (article) { return article.id === Number(button.dataset.id); });
      document.getElementById("admin-article-id").value = item.id;
      document.getElementById("admin-article-title").value = item.title;
      document.getElementById("admin-article-slug").value = item.slug;
      document.getElementById("admin-article-summary").value = item.summary || "";
      document.getElementById("admin-article-content").value = item.content;
      document.getElementById("admin-article-published").checked = item.is_published;
    });
  });

  Array.from(document.querySelectorAll(".delete-article")).forEach(function (button) {
    button.addEventListener("click", async function () {
      try {
        await window.PetShop.api.request("/admin/articles/" + button.dataset.id, { method: "DELETE" });
        window.PetShop.ui.toast("Đã xóa bài viết");
        loadAdminArticles();
      } catch (error) {
        window.PetShop.ui.toast(error.message, "error");
      }
    });
  });
}
