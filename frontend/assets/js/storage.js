(function () {
  var keys = {
    token: "pet_shop_access_token",
    user: "pet_shop_current_user",
  };

  function getToken() {
    return localStorage.getItem(keys.token);
  }

  function setToken(token) {
    if (token) {
      localStorage.setItem(keys.token, token);
      return;
    }
    localStorage.removeItem(keys.token);
  }

  function getUser() {
    var value = localStorage.getItem(keys.user);
    return value ? JSON.parse(value) : null;
  }

  function setUser(user) {
    if (user) {
      localStorage.setItem(keys.user, JSON.stringify(user));
      return;
    }
    localStorage.removeItem(keys.user);
  }

  function clearAuth() {
    localStorage.removeItem(keys.token);
    localStorage.removeItem(keys.user);
  }

  window.PetShop = window.PetShop || {};
  window.PetShop.storage = {
    getToken: getToken,
    setToken: setToken,
    getUser: getUser,
    setUser: setUser,
    clearAuth: clearAuth,
  };
})();
