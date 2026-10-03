const API_BASE = "http://localhost:8000/api";

export async function fetchFunnel() {
    const res = await fetch(`${API_BASE}/funnel`);
    return res.json();
}

export async function fetchCases() {
    const res = await fetch(`${API_BASE}/cases`);
    return res.json();
}

export async function fetchCase(id) {
    const res = await fetch(`${API_BASE}/cases/${id}`);
    return res.json();
}

export async function fetchSweep() {
    const res = await fetch(`${API_BASE}/sweep`);
    return res.json();
}
