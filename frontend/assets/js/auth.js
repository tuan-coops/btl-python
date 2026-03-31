(function () {
  async function fetchCurrentUser() {
    var user = await window.PetShop.api.request("/auth/me");
    window.PetShop.storage.setUser(user);
    return user;
  }

  async function login(payload) {
    var result = await window.PetShop.api.request("/auth/login", {
      method: "POST",
      auth: false,
      body: payload,
    });
    window.PetShop.storage.setToken(result.access_token);
    window.PetShop.storage.setUser(result.user);
    return result;
  }

  async function register(payload) {
    return window.PetShop.api.request("/auth/register", {
      method: "POST",
      auth: false,
      body: payload,
    });
  }

  function logout() {
    window.PetShop.storage.clearAuth();
  }

  function isSeller() {
    var user = window.PetShop.storage.getUser();
    return user && user.role && user.role.name === "seller";
  }

  window.PetShop = window.PetShop || {};
  window.PetShop.auth = {
    fetchCurrentUser: fetchCurrentUser,
    login: login,
    register: register,
    logout: logout,
    isSeller: isSeller,
  };
})();
