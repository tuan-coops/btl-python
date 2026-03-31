(function () {
  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatCurrency(value) {
    var amount = Number(value || 0);
    return amount.toLocaleString("vi-VN") + " đ";
  }

  function formatDateTime(value) {
    if (!value) {
      return "--";
    }
    return new Date(value).toLocaleString("vi-VN");
  }

  function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function toast(message, type) {
    var wrap = document.getElementById("toast-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.id = "toast-wrap";
      wrap.className = "toast-wrap";
      document.body.appendChild(wrap);
    }

    var el = document.createElement("div");
    el.className = "toast" + (type ? " " + type : "");
    el.textContent = message;
    wrap.appendChild(el);
    setTimeout(function () {
      el.remove();
    }, 3200);
  }

  function setLoading(target, loadingText) {
    if (!target) {
      return function () {};
    }
    var original = target.innerHTML;
    target.innerHTML = loadingText || "Đang tải...";
    return function () {
      target.innerHTML = original;
    };
  }

  function setButtonLoading(button, loading, loadingText) {
    if (!button) {
      return;
    }
    if (loading) {
      button.dataset.originalText = button.innerHTML;
      button.innerHTML = loadingText || "Đang xử lý...";
      button.disabled = true;
      button.classList.add("is-loading");
      return;
    }
    button.innerHTML = button.dataset.originalText || button.innerHTML;
    button.disabled = false;
    button.classList.remove("is-loading");
  }

  function emptyState(message) {
    return '<div class="empty-state">' + escapeHtml(message) + "</div>";
  }

  function renderPagination(target, meta, onChange) {
    if (!target || !meta || meta.total <= meta.page_size) {
      if (target) {
        target.innerHTML = "";
      }
      return;
    }

    target.innerHTML =
      '<div class="pagination">' +
      '<button class="button-ghost" data-page="' + (meta.page - 1) + '"' + (meta.page <= 1 ? " disabled" : "") + ">Truoc</button>" +
      "<span>Trang " + meta.page + " / " + Math.max(1, Math.ceil(meta.total / meta.page_size)) + "</span>" +
      '<button class="button-ghost" data-page="' + (meta.page + 1) + '"' + (meta.page * meta.page_size >= meta.total ? " disabled" : "") + ">Sau</button>" +
      "</div>";

    Array.from(target.querySelectorAll("[data-page]")).forEach(function (button) {
      button.addEventListener("click", function () {
        if (button.disabled) {
          return;
        }
        onChange(Number(button.dataset.page));
      });
    });
  }

  function renderStatus(status) {
    var value = String(status || "");
    return '<span class="status ' + escapeHtml(value) + '">' + escapeHtml(value) + "</span>";
  }

  function clearFormErrors(form) {
    if (!form) {
      return;
    }
    Array.from(form.querySelectorAll(".field-error")).forEach(function (node) {
      node.remove();
    });
    Array.from(form.querySelectorAll(".field input, .field textarea, .field select")).forEach(function (input) {
      input.classList.remove("input-error");
    });
  }

  function showFieldError(input, message) {
    if (!input) {
      return;
    }
    input.classList.add("input-error");
    var field = input.closest(".field");
    if (!field) {
      return;
    }
    var error = field.querySelector(".field-error");
    if (!error) {
      error = document.createElement("div");
      error.className = "field-error";
      field.appendChild(error);
    }
    error.textContent = message;
  }

  function validateForm(rules) {
    var valid = true;
    rules.forEach(function (rule) {
      var input = document.getElementById(rule.id);
      if (!input) {
        return;
      }
      var rawValue = input.type === "checkbox" ? input.checked : String(input.value || "").trim();
      if (rule.required && !rawValue) {
        showFieldError(input, rule.label + " không được để trống");
        valid = false;
        return;
      }
      if (!rawValue) {
        return;
      }
      if (rule.type === "email") {
        var emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(rawValue);
        if (!emailOk) {
          showFieldError(input, rule.label + " không hợp lệ");
          valid = false;
          return;
        }
      }
      if (rule.minLength && String(rawValue).length < rule.minLength) {
        showFieldError(input, rule.label + " phải có ít nhất " + rule.minLength + " ký tự");
        valid = false;
        return;
      }
      if (rule.min != null && Number(rawValue) < rule.min) {
        showFieldError(input, rule.label + " không hợp lệ");
        valid = false;
        return;
      }
    });
    return valid;
  }

  function prepareFormSubmit(form, button, rules) {
    clearFormErrors(form);
    if (!validateForm(rules || [])) {
      toast("Vui lòng kiểm tra lại dữ liệu nhập", "error");
      return false;
    }
    setButtonLoading(button, true);
    return true;
  }

  function finishFormSubmit(button) {
    setButtonLoading(button, false);
  }

  window.PetShop = window.PetShop || {};
  window.PetShop.ui = {
    escapeHtml: escapeHtml,
    formatCurrency: formatCurrency,
    formatDateTime: formatDateTime,
    getQueryParam: getQueryParam,
    toast: toast,
    emptyState: emptyState,
    renderPagination: renderPagination,
    renderStatus: renderStatus,
    setLoading: setLoading,
    setButtonLoading: setButtonLoading,
    clearFormErrors: clearFormErrors,
    showFieldError: showFieldError,
    validateForm: validateForm,
    prepareFormSubmit: prepareFormSubmit,
    finishFormSubmit: finishFormSubmit,
  };
})();
