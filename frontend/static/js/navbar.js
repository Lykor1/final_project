document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    if (Auth.isAuthenticated()) {
        navbar.innerHTML = `
            <li><a href="${URLS.index}">Главная</a></li>
            <li><a href="${URLS.profile}">Профиль</a></li>
            <li><a href="#" id="logout-link">Выход</a></li>
        `;

        document
            .getElementById('logout-link')
            .addEventListener('click', async (e) => {
                e.preventDefault();
                await logout();
            });

    } else {
        navbar.innerHTML = `
            <li><a href="${URLS.index}">Главная</a></li>
            <li><a href="${URLS.register}">Регистрация</a></li>
            <li><a href="${URLS.login}">Вход</a></li>
        `;
    }
});

async function logout() {
    const refresh = Auth.getRefresh();

    if (refresh) {
        await fetch(URLS.logout, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${Auth.getAccess()}`
            },
            body: JSON.stringify({refresh})
        });
    }

    Auth.logout();
    window.location.href = URLS.index;
}
