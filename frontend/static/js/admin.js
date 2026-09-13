(() => {
  const API_BASE = "";

  const gate = document.getElementById("gate");
  const dashboard = document.getElementById("dashboard");
  const adminKeyInput = document.getElementById("admin-key");
  const gateBtn = document.getElementById("gate-btn");
  const gateError = document.getElementById("gate-error");

  const searchInput = document.getElementById("search-input");
  const dateInput = document.getElementById("date-input");
  const filterBtn = document.getElementById("filter-btn");
  const resetBtn = document.getElementById("reset-btn");
  const exportBtn = document.getElementById("export-btn");

  const bookingsBody = document.getElementById("bookings-body");
  const emptyState = document.getElementById("empty-state");

  let adminKey = sessionStorage.getItem("aster_admin_key") || "";

  function headers() {
    return { "X-Admin-Key": adminKey };
  }

  async function tryUnlock(key) {
    const res = await fetch(`${API_BASE}/api/bookings`, { headers: { "X-Admin-Key": key } });
    if (res.ok) {
      adminKey = key;
      sessionStorage.setItem("aster_admin_key", key);
      gate.hidden = true;
      dashboard.hidden = false;
      renderBookings(await res.json());
      return true;
    }
    return false;
  }

  gateBtn.addEventListener("click", async () => {
    const key = adminKeyInput.value.trim();
    if (!key) return;
    const ok = await tryUnlock(key);
    gateError.hidden = ok;
  });

  adminKeyInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") gateBtn.click();
  });

  function renderBookings(rows) {
    bookingsBody.innerHTML = "";
    emptyState.hidden = rows.length > 0;

    for (const b of rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>#${b.id}</td>
        <td>${escapeHtml(b.name)}</td>
        <td>${escapeHtml(b.email)}</td>
        <td>${escapeHtml(b.phone)}</td>
        <td>${escapeHtml(b.booking_type)}</td>
        <td>${escapeHtml(b.date)}</td>
        <td>${escapeHtml(b.time)}</td>
        <td><span class="pill ${b.status}">${b.status}</span></td>
        <td></td>
      `;
      if (b.status !== "cancelled") {
        const btn = document.createElement("button");
        btn.className = "cancel-btn";
        btn.textContent = "Cancel";
        btn.addEventListener("click", () => cancelBooking(b.id));
        tr.lastElementChild.appendChild(btn);
      }
      bookingsBody.appendChild(tr);
    }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  }

  async function fetchBookings() {
    const params = new URLSearchParams();
    if (searchInput.value.trim()) params.set("search", searchInput.value.trim());
    if (dateInput.value) params.set("date", dateInput.value);

    const res = await fetch(`${API_BASE}/api/bookings?${params.toString()}`, { headers: headers() });
    if (!res.ok) return;
    renderBookings(await res.json());
  }

  async function cancelBooking(id) {
    if (!confirm(`Cancel booking #${id}?`)) return;
    await fetch(`${API_BASE}/api/bookings/${id}`, { method: "DELETE", headers: headers() });
    fetchBookings();
  }

  filterBtn.addEventListener("click", fetchBookings);
  resetBtn.addEventListener("click", () => {
    searchInput.value = "";
    dateInput.value = "";
    fetchBookings();
  });

  exportBtn.addEventListener("click", async () => {
    const res = await fetch(`${API_BASE}/api/bookings/export`, { headers: headers() });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "bookings.csv";
    a.click();
    URL.revokeObjectURL(url);
  });

  // Auto-unlock if a key is already stored for this browser session
  if (adminKey) {
    tryUnlock(adminKey);
  }
})();
