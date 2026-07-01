const API_BASE = "https://noted-tfej.onrender.com/";
const TOKEN_KEY = "noted_token";

const views = {
  auth: document.getElementById("auth-view"),
  dashboard: document.getElementById("dashboard-view"),
  editor: document.getElementById("editor-view"),
  shared: document.getElementById("shared-view"),
  confirm: document.getElementById("confirm-view"),
};

let currentPage = 1;
let totalPages = 1;
let currentNoteId = null;
let sharedContext = null;

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function logout() {
  clearToken();
  currentNoteId = null;
  navigate("#login");
}

function showView(name) {
  Object.values(views).forEach((v) => v.classList.add("hidden"));
  views[name].classList.remove("hidden");
}

function setError(el, msg) {
  el.textContent = msg || "";
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();

  if (options.auth !== false && token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const text = await res.text();

  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const detail = data?.detail || (typeof data === "string" ? data : "Request failed");
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function updateCharCount(textarea, counterEl) {
  const len = textarea.value.length;
  counterEl.textContent = `${len}/300`;
  counterEl.classList.toggle("over", len > 300);
}

function navigate(hash) {
  window.location.hash = hash;
}

function parseRoute() {
  const hash = window.location.hash.slice(1) || "";
  const parts = hash.split("/").filter(Boolean);

  if (parts[0] === "shared" && parts.length >= 3) {
    return { view: "shared", id: parts[1], token: parts[2] };
  }
  if (parts[0] === "confirm" && parts.length >= 2) {
    return { view: "confirm", token: parts[1] };
  }
  if (parts[0] === "note") {
    return { view: "editor", id: parts[1] === "new" ? null : parts[1] };
  }
  if (parts[0] === "register") {
    return { view: "auth", tab: "register" };
  }
  if (parts[0] === "login" || !getToken()) {
    return { view: "auth", tab: "login" };
  }
  return { view: "dashboard" };
}

async function handleRoute() {
  const route = parseRoute();

  if (route.view === "confirm") {
    showView("confirm");
    await confirmEmail(route.token);
    return;
  }

  if (route.view === "auth") {
    showView("auth");
    switchAuthTab(route.tab || "login");
    return;
  }

  if (!getToken()) {
    navigate("#login");
    return;
  }

  if (route.view === "dashboard") {
    showView("dashboard");
    await loadDashboard(currentPage);
    return;
  }

  if (route.view === "editor") {
    showView("editor");
    await openEditor(route.id);
    return;
  }

  if (route.view === "shared") {
    showView("shared");
    await openSharedNote(route.id, route.token);
  }
}

function switchAuthTab(tab) {
  document.querySelectorAll(".auth-tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });
  document.getElementById("login-form").classList.toggle("hidden", tab !== "login");
  document.getElementById("register-form").classList.toggle("hidden", tab !== "register");
  setError(document.getElementById("login-error"), "");
  setError(document.getElementById("register-error"), "");
}

function showRegisterModal(message) {
  document.getElementById("register-modal-message").textContent = message;
  document.getElementById("register-modal").classList.remove("hidden");
}

function closeRegisterModal() {
  document.getElementById("register-modal").classList.add("hidden");
  switchAuthTab("login");
  navigate("#login");
}

async function confirmEmail(token) {
  const resultEl = document.getElementById("confirm-result");
  const loginBtn = document.getElementById("confirm-login-btn");
  resultEl.className = "confirm-result";
  loginBtn.classList.add("hidden");
  resultEl.innerHTML = '<p class="confirm-status">Confirming your email...</p>';

  try {
    const data = await api(`/confirm/${encodeURIComponent(token)}`, { auth: false });
    resultEl.classList.add("success");
    resultEl.innerHTML = `<p class="confirm-status">${escapeHtml(data.message)}</p>`;
    loginBtn.classList.remove("hidden");
  } catch (e) {
    resultEl.classList.add("error");
    resultEl.innerHTML = `<p class="confirm-status">${escapeHtml(e.message)}</p>`;
    loginBtn.classList.remove("hidden");
  }
}

async function login(email, password) {
  const data = await api("/login", {
    auth: false,
    method: "POST",
    body: { email, password },
  });
  setToken(data.acess_token);
  navigate("#dashboard");
}

async function register(email, password) {
  return api("/register", {
    auth: false,
    method: "POST",
    body: { email, password },
  });
}

async function loadDashboard(page) {
  const grid = document.getElementById("notes-grid");
  const errEl = document.getElementById("dashboard-error");
  setError(errEl, "");
  grid.innerHTML = '<p class="empty-state">Loading...</p>';

  try {
    const res = await api(`/notes?page=${page}&limit=3`);
    currentPage = res.page;
    totalPages = res["total pages"] || 1;

    document.getElementById("page-info").textContent =
      `Page ${currentPage} of ${totalPages} (${res.total} notes)`;
    document.getElementById("prev-page").disabled = currentPage <= 1;
    document.getElementById("next-page").disabled = currentPage >= totalPages;

    grid.innerHTML = "";

    if (!res.data || res.data.length === 0) {
      grid.innerHTML = '<p class="empty-state">No notes yet. Create your first one!</p>';
      return;
    }

    res.data.forEach((note) => {
      const card = document.createElement("div");
      card.className = "note-card";
      card.innerHTML = `
        <div class="note-card-title">${escapeHtml(note.title)}</div>
        <div class="note-card-preview">${escapeHtml(note.body)}</div>
        <div class="note-card-date">${formatDate(note.doc)}</div>
      `;
      card.addEventListener("click", () => navigate(`#note/${note.id}`));
      grid.appendChild(card);
    });
  } catch (e) {
    if (e.message.includes("expired") || e.message.includes("token")) {
      clearToken();
      navigate("#login");
      return;
    }
    setError(errEl, e.message);
    grid.innerHTML = "";
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function openEditor(id) {
  currentNoteId = id ? Number(id) : null;
  const titleEl = document.getElementById("note-title");
  const bodyEl = document.getElementById("note-body");
  const dateEl = document.getElementById("note-date");
  const shareBtn = document.getElementById("share-btn");
  const deleteBtn = document.getElementById("delete-btn");
  const errEl = document.getElementById("editor-error");
  const successEl = document.getElementById("editor-success");

  setError(errEl, "");
  setError(successEl, "");
  titleEl.value = "";
  bodyEl.value = "";
  dateEl.textContent = "";
  updateCharCount(bodyEl, document.getElementById("char-count"));

  const isNew = !currentNoteId;
  shareBtn.classList.toggle("hidden", isNew);
  deleteBtn.classList.toggle("hidden", isNew);

  if (isNew) {
    dateEl.textContent = formatDate(new Date().toISOString());
    return;
  }

  try {
    const note = await api(`/notes/${currentNoteId}`);
    titleEl.value = note.title;
    bodyEl.value = note.body;
    dateEl.textContent = formatDate(note.doc);
    updateCharCount(bodyEl, document.getElementById("char-count"));
  } catch (e) {
    setError(errEl, e.message);
  }
}

async function saveNote() {
  const title = document.getElementById("note-title").value.trim();
  const body = document.getElementById("note-body").value;
  const errEl = document.getElementById("editor-error");
  const successEl = document.getElementById("editor-success");
  setError(errEl, "");
  setError(successEl, "");

  if (!title) {
    setError(errEl, "Title is required.");
    return;
  }
  if (body.length > 300) {
    setError(errEl, "Note body must be 300 characters or less.");
    return;
  }

  try {
    if (currentNoteId) {
      await api("/notes", {
        method: "PATCH",
        body: { id: currentNoteId, title, body },
      });
      setError(successEl, "Note updated.");
    } else {
      const created = await api("/notes", {
        method: "POST",
        body: { title, body },
      });
      currentNoteId = created.id;
      document.getElementById("share-btn").classList.remove("hidden");
      document.getElementById("delete-btn").classList.remove("hidden");
      document.getElementById("note-date").textContent = formatDate(created.doc);
      navigate(`#note/${created.id}`);
      setError(successEl, "Note created.");
    }
  } catch (e) {
    setError(errEl, e.message);
  }
}

async function deleteNote() {
  if (!currentNoteId) return;
  if (!confirm("Delete this note?")) return;

  const errEl = document.getElementById("editor-error");
  setError(errEl, "");

  try {
    await api("/notes", {
      method: "DELETE",
      body: { id: currentNoteId },
    });
    navigate("#dashboard");
  } catch (e) {
    setError(errEl, e.message);
  }
}

function openShareModal() {
  document.getElementById("share-modal").classList.remove("hidden");
  document.getElementById("allow-edit").checked = false;
  document.getElementById("share-link").classList.remove("visible");
  document.getElementById("share-link").textContent = "";
  document.getElementById("share-copy").classList.add("hidden");
  setError(document.getElementById("share-error"), "");
}

function closeShareModal() {
  document.getElementById("share-modal").classList.add("hidden");
}

async function generateShareLink() {
  const allowEdit = document.getElementById("allow-edit").checked;
  const errEl = document.getElementById("share-error");
  const linkEl = document.getElementById("share-link");
  setError(errEl, "");

  try {
    const url = await api(`/notes/${currentNoteId}/share`, {
      auth: false,
      method: "POST",
      body: { edit: allowEdit },
    });

    const token = String(url).split("/shared/")[1];
    const frontendUrl = `${window.location.origin}${window.location.pathname}#/shared/${currentNoteId}/${token}`;

    linkEl.textContent = frontendUrl;
    linkEl.classList.add("visible");
    linkEl.dataset.url = frontendUrl;
    document.getElementById("share-copy").classList.remove("hidden");
  } catch (e) {
    setError(errEl, e.message);
  }
}

async function openSharedNote(id, token) {
  sharedContext = { id: Number(id), token };
  const errEl = document.getElementById("shared-error");
  const successEl = document.getElementById("shared-success");
  setError(errEl, "");
  setError(successEl, "");

  try {
    const note = await api(`/notes/${id}/shared/${token}`, { auth: false });
    document.getElementById("shared-title").textContent = note.title;
    document.getElementById("shared-date").textContent = formatDate(note.doc);

    const bodyEl = document.getElementById("shared-body");
    bodyEl.value = note.body;
    updateCharCount(bodyEl, document.getElementById("shared-char-count"));

    const canEdit = await checkSharedEdit(token);
    bodyEl.readOnly = !canEdit;
    document.getElementById("shared-save-btn").classList.toggle("hidden", !canEdit);
  } catch (e) {
    setError(errEl, e.message);
  }
}

function decodeJwtPayload(token) {
  const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(base64));
}

async function checkSharedEdit(token) {
  try {
    const payload = decodeJwtPayload(token);
    return payload.edit === true;
  } catch {
    return false;
  }
}

async function saveSharedNote() {
  if (!sharedContext) return;
  const body = document.getElementById("shared-body").value;
  const errEl = document.getElementById("shared-error");
  const successEl = document.getElementById("shared-success");
  setError(errEl, "");
  setError(successEl, "");

  try {
    await api(`/notes/${sharedContext.id}/shared/${sharedContext.token}`, {
      auth: false,
      method: "PATCH",
      body: { id: sharedContext.id, body },
    });
    setError(successEl, "Shared note updated.");
  } catch (e) {
    setError(errEl, e.message);
  }
}

document.querySelectorAll(".auth-tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    switchAuthTab(btn.dataset.tab);
    navigate(`#${btn.dataset.tab}`);
  });
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("login-error");
  setError(errEl, "");
  try {
    await login(
      document.getElementById("login-email").value.trim(),
      document.getElementById("login-password").value
    );
  } catch (err) {
    setError(errEl, err.message);
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("register-error");
  setError(errEl, "");
  try {
    const data = await register(
      document.getElementById("register-email").value.trim(),
      document.getElementById("register-password").value
    );
    document.getElementById("register-form").reset();
    showRegisterModal(data.message);
  } catch (err) {
    setError(errEl, err.message);
  }
});

document.getElementById("register-modal-ok").addEventListener("click", closeRegisterModal);
document.getElementById("register-modal").addEventListener("click", (e) => {
  if (e.target.id === "register-modal") closeRegisterModal();
});
document.getElementById("confirm-login-btn").addEventListener("click", () => navigate("#login"));

document.getElementById("new-note-btn").addEventListener("click", () => navigate("#note/new"));
document.getElementById("logout-btn").addEventListener("click", logout);

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "n") {
    if (!getToken() || views.dashboard.classList.contains("hidden")) return;
    e.preventDefault();
    navigate("#note/new");
  }
});
document.getElementById("back-btn").addEventListener("click", () => navigate("#dashboard"));
document.getElementById("save-btn").addEventListener("click", saveNote);
document.getElementById("delete-btn").addEventListener("click", deleteNote);
document.getElementById("share-btn").addEventListener("click", openShareModal);
document.getElementById("share-cancel").addEventListener("click", closeShareModal);
document.getElementById("share-generate").addEventListener("click", generateShareLink);

document.getElementById("share-copy").addEventListener("click", () => {
  const url = document.getElementById("share-link").dataset.url;
  if (url) navigator.clipboard.writeText(url);
});

document.getElementById("prev-page").addEventListener("click", () => {
  if (currentPage > 1) loadDashboard(currentPage - 1);
});

document.getElementById("next-page").addEventListener("click", () => {
  if (currentPage < totalPages) loadDashboard(currentPage + 1);
});

document.getElementById("note-body").addEventListener("input", (e) => {
  updateCharCount(e.target, document.getElementById("char-count"));
});

document.getElementById("shared-body").addEventListener("input", (e) => {
  updateCharCount(e.target, document.getElementById("shared-char-count"));
});

document.getElementById("shared-save-btn").addEventListener("click", saveSharedNote);

document.getElementById("share-modal").addEventListener("click", (e) => {
  if (e.target.id === "share-modal") closeShareModal();
});

window.addEventListener("hashchange", handleRoute);
handleRoute();
