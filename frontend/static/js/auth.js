const Auth = {
    getAccess() {
        return localStorage.getItem('access');
    },

    getRefresh() {
        return localStorage.getItem('refresh');
    },

    isAuthenticated() {
        return !!this.getAccess();
    },

    login(access, refresh) {
        localStorage.setItem('access', access);
        localStorage.setItem('refresh', refresh);
    },

    logout() {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
    }
};
