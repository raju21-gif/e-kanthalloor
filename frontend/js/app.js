const API_URL = "https://e-kanthalloor.onrender.com";

const API = {
    async request(endpoint, method = "GET", body = null, auth = true) {
        const headers = {};
        if (auth) {
            const token = localStorage.getItem("token");
            if (token) headers["Authorization"] = `Bearer ${token}`;
        }

        const config = { method, headers };

        if (body) {
            if (body instanceof FormData) {
                // Let browser set Content-Type for FormData (multipart/form-data)
                config.body = body;
            } else {
                headers["Content-Type"] = "application/json";
                config.body = JSON.stringify(body);
            }
        }

        try {
            console.log(`[API] Request: ${method} ${API_URL}${endpoint}`);
            const res = await fetch(`${API_URL}${endpoint}`, config);
            const data = await res.json();
            console.log(`[API] Response:`, data);
            if (!res.ok) throw new Error(data.detail || "Something went wrong");
            return data;
        } catch (err) {
            console.error(err);
            alert(err.message);
            throw err;
        }
    },

    login: (username, password) => {
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);
        return fetch(`${API_URL}/auth/token`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        }).then(res => res.json());
    },

    register: (data) => API.request("/auth/register", "POST", data, false),
    getMe: () => API.request("/auth/me", "GET", null, true),
    updateProfile: (data) => API.request("/auth/profile", "PATCH", data, true),
    getSchemes: (lang = "en") => API.request(`/schemes/?language=${lang}`),

    // Admin specific
    createScheme: (data) => API.request("/schemes/", "POST", data),
    getScheme: (id) => API.request(`/schemes/${id}`),
    getAdminStats: () => API.request("/admin/stats", "GET", null, true),
    getAdminUsers: () => API.request("/admin/users", "GET", null, true),
    getPendingApplications: () => API.request("/admin/applications/pending", "GET", null, true),
    verifyApplication: (id) => API.request(`/admin/verify-application/${id}`, "POST", null, true),
    rejectApplication: (id) => API.request(`/admin/reject-application/${id}`, "POST", null, true),
    deleteAllPendingApplications: () => API.request("/admin/applications/pending", "DELETE", null, true),

    chat: (message) => API.request("/api/chat", "POST", { message }, true),
    submitInfo: (data) => API.request("/info/submit", "POST", data, true),


    // Applications
    applyScheme: (data) => API.request("/applications/apply", "POST", data, true),
    getMyApplications: () => API.request("/applications/my-applications", "GET", null, true)
};

const UI = {
    renderSchemes: (schemes, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (schemes.length === 0) {
            container.innerHTML = '<p style="color:var(--text-gray)">No schemes found.</p>';
            return;
        }

        container.innerHTML = schemes.map(s => `
            <div class="card scheme-card animate-fade-in" style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--glass-border);">
                <div>
                    <h3 style="margin-bottom: 0.5rem; color: var(--primary-color);">${s.name}</h3>
                    <p style="color: var(--text-gray); font-size: 0.9em; margin-bottom: 1rem;">${s.description}</p>
                    
                    <div style="font-size: 0.8em; margin-bottom: 0.5rem;">
                        <strong>Beneficiaries:</strong> ${s.beneficiary_category ? s.beneficiary_category.join(", ") : 'General'}
                    </div>
                </div>
                <button onclick="viewSchemeDetails('${s._id}')" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.85em; margin-top: 1rem; width: 100%;">
                    View Details
                </button>
            </div>
        `).join("");
    }
};

function viewSchemeDetails(id) {
    window.location.href = `scheme_details.html?id=${id}`;
}

window.API = API;
window.UI = UI;
window.viewSchemeDetails = viewSchemeDetails;
