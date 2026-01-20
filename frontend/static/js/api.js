async function fetchWithAuth(url, options = {}) {
    if (!options.headers) {
        options.headers = {};
    }

    options.headers['Authorization'] = `Bearer ${Auth.getAccess()}`;

    let response = await fetch(url, options);

    if (response.status !== 401) {
        return response;
    }

    const refreshed = await Auth.refreshAccessToken();

    if (!refreshed) {
        window.location.href = URLS.login;
        throw new Error('Unauthorized');
    }

    options.headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
    return fetch(url, options);
}
