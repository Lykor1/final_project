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

    setTokens(access, refresh) {
        localStorage.setItem('access', access);
        if (refresh) {
            localStorage.setItem('refresh', refresh);
        }
    },

    logout() {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
    },

    async refreshAccessToken() {
        const refresh = this.getRefresh();
        if (!refresh) {
            this.logout();
            return false;
        }

        const response = await fetch(URLS.refreshAPI, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });

        if (!response.ok) {
            this.logout();
            return false;
        }

        const data = await response.json();
        this.setTokens(data.access, data.refresh);
        return true;
    }
};
