(function () {
  var defaultApiBaseUrl = "http://127.0.0.1:8000/api/v1";
  var storageKey = "pet_shop_api_base_url";

  function getApiBaseUrl() {
    return localStorage.getItem(storageKey) || defaultApiBaseUrl;
  }

  function setApiBaseUrl(value) {
    if (!value) {
      localStorage.removeItem(storageKey);
      return;
    }
    localStorage.setItem(storageKey, value.replace(/\/+$/, ""));
  }

  function getRootPrefix() {
    return window.location.pathname.indexOf("/pages/") >= 0 ? "../" : "./";
  }

  window.PetShop = window.PetShop || {};
  window.PetShop.config = {
    defaultApiBaseUrl: defaultApiBaseUrl,
    getApiBaseUrl: getApiBaseUrl,
    setApiBaseUrl: setApiBaseUrl,
    getRootPrefix: getRootPrefix,
  };
})();
