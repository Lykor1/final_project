async function loadCurrentUser() {
    const response = await fetchWithAuth(URLS.userDetailAPI);

    if (!response.ok) {
        Auth.logout();
        return null;
    }

    const data = await response.json();
    APP.user = data;
    return data;
}
