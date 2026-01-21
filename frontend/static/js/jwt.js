function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(base64));
    } catch {
        return null;
    }
}

function getJwtPayload() {
    const token = Auth.getAccess();
    if (!token) return null;
    return parseJwt(token);
}
