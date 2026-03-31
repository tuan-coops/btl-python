(function () {
  function extractErrorMessage(payload) {
    if (!payload) {
      return "Yêu cầu thất bại";
    }
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    if (Array.isArray(payload.errors) && payload.errors.length) {
      return payload.errors.map(function (item) {
        return item.msg || JSON.stringify(item);
      }).join(", ");
    }
    if (Array.isArray(payload.detail) && payload.detail.length) {
      return payload.detail.map(function (item) {
        return item.msg || JSON.stringify(item);
      }).join(", ");
    }
    return payload.message || "Yêu cầu thất bại";
  }

  function handleAuthFailure(status, options) {
    var isAuthRequest = (options.path || "").indexOf("/auth/login") === 0 || (options.path || "").indexOf("/auth/register") === 0;
    if (status !== 401 || isAuthRequest) {
      return;
    }

    if (window.PetShop && window.PetShop.storage) {
      window.PetShop.storage.clearAuth();
    }

    if (window.PetShop && window.PetShop.ui) {
      window.PetShop.ui.toast("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", "error");
    }
  }

  async function request(path, options) {
    options = options || {};
    options.path = path;

    var headers = Object.assign(
      {
        Accept: "application/json",
      },
      options.headers || {}
    );

    if (options.body !== undefined && !(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    if (options.auth !== false) {
      var token = window.PetShop.storage.getToken();
      if (token) {
        headers.Authorization = "Bearer " + token;
      }
    }

    var response;
    try {
      response = await fetch(window.PetShop.config.getApiBaseUrl() + path, {
        method: options.method || "GET",
        headers: headers,
        body:
          options.body === undefined
            ? undefined
            : options.body instanceof FormData
              ? options.body
              : JSON.stringify(options.body),
      });
    } catch (networkError) {
      var offlineError = new Error("Không kết nối được tới backend. Hãy kiểm tra server FastAPI và API base URL.");
      offlineError.status = 0;
      throw offlineError;
    }

    var payload = null;
    var text = await response.text();
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch (error) {
        payload = { detail: text };
      }
    }

    if (!response.ok) {
      handleAuthFailure(response.status, options);
      var err = new Error(extractErrorMessage(payload));
      err.status = response.status;
      err.payload = payload;
      throw err;
    }

    return payload;
  }

  window.PetShop = window.PetShop || {};
  window.PetShop.api = {
    request: request,
    extractErrorMessage: extractErrorMessage,
  };
})();
