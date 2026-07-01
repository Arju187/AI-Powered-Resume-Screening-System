/**
 * Shared UI helpers used across every page: toast notifications, navbar
 * state (avatar/dropdown/disabled dashboard link), the signature ATS gauge,
 * and small formatting utilities.
 */

function showToast(message, type = "info") {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    document.body.appendChild(stack);
  }
  const toast = document.createElement("div");
  toast.className = `os-toast ${type}`;
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3800);
}

function initials(name) {
  if (!name) return "?";
  return name.trim().charAt(0).toUpperCase();
}

function timeAgo(isoString) {
  const diffMs = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(isoString).toLocaleDateString();
}

function formatDate(isoString) {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function statusLabel(status) {
  return status.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

/** Renders the radial "ATS Score" gauge — the product's signature visual element. */
function renderAtsGauge(container, score, { size = "md" } = {}) {
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score || 0));
  const offset = circumference - (pct / 100) * circumference;
  const sizeClass = size === "sm" ? "sm" : "";

  container.innerHTML = `
    <div class="ats-gauge ${sizeClass}">
      <svg viewBox="0 0 120 120" width="100%" height="100%">
        <circle class="track" cx="60" cy="60" r="${radius}"></circle>
        <circle class="fill" cx="60" cy="60" r="${radius}"
          stroke-dasharray="${circumference}" stroke-dashoffset="${circumference}"></circle>
      </svg>
      <div class="readout">
        <div class="score">${Math.round(pct)}</div>
        <div class="label">ATS SCORE</div>
      </div>
    </div>`;

  // animate after insertion
  requestAnimationFrame(() => {
    const fillCircle = container.querySelector(".fill");
    if (fillCircle) fillCircle.style.strokeDashoffset = offset;
  });
}

/** Builds the shared navbar. Call on every page with the current page's nav key. */
function renderNavbar(activeKey = "") {
  const mount = document.getElementById("os-navbar-mount");
  if (!mount) return;

  const loggedIn = Auth.isLoggedIn();
  const role = Auth.getRole();
  const name = Auth.getName();

  const dashboardHref = role === "admin" ? "admin-dashboard.html" : "candidate-dashboard.html";
  const dashboardClass = loggedIn ? "" : "disabled";

  const publicLinks = `
    <a href="jobs.html" class="${activeKey === 'jobs' ? 'active' : ''}">Jobs</a>
    <a href="${dashboardHref}" class="${dashboardClass} ${activeKey === 'dashboard' ? 'active' : ''}">Dashboard</a>
  `;

  let rightSide = "";
  if (loggedIn) {
    rightSide = `
      <div class="dropdown">
        <div class="os-avatar" data-bs-toggle="dropdown" aria-expanded="false" role="button" title="${name}">
          ${initials(name)}
        </div>
        <ul class="dropdown-menu dropdown-menu-end shadow-sm" style="border-radius: 10px; border-color: var(--line);">
          <li><h6 class="dropdown-header">${name}</h6></li>
          ${role === "candidate" ? `
            <li><a class="dropdown-item" href="profile.html"><i class="fa-regular fa-user me-2"></i>Profile</a></li>
            <li><a class="dropdown-item" href="applications.html"><i class="fa-regular fa-bookmark me-2"></i>My Applications</a></li>
          ` : `
            <li><a class="dropdown-item" href="admin-dashboard.html"><i class="fa-solid fa-gauge me-2"></i>Admin Dashboard</a></li>
          `}
          <li><hr class="dropdown-divider"></li>
          <li><a class="dropdown-item text-danger" href="#" id="navLogoutBtn"><i class="fa-solid fa-arrow-right-from-bracket me-2"></i>Logout</a></li>
        </ul>
      </div>`;
  } else {
    rightSide = `
      <a href="login.html" class="btn-ghost-light">Log in</a>
      <a href="register.html" class="btn-os-primary">Register</a>
    `;
  }

  mount.innerHTML = `
    <nav class="os-navbar">
      <a href="index.html" class="brand text-decoration-none">
        <span class="dot"></span> AI Powered Resume Screening  <span class="sub"></span>
      </a>
      <div class="os-navlinks d-none d-md-flex">${publicLinks}</div>
      <div class="d-flex align-items-center gap-3">${rightSide}</div>
    </nav>`;

  const logoutBtn = document.getElementById("navLogoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", (e) => { e.preventDefault(); Auth.logout(); });
}

/** Renders the dashboard sidebar (candidate or admin) into #os-sidebar-mount. */
function renderSidebar(activeKey = "") {
  const mount = document.getElementById("os-sidebar-mount");
  if (!mount) return;
  const role = Auth.getRole();

  const candidateLinks = `
    <div class="nav-section-label">Workspace</div>
    <a href="candidate-dashboard.html" class="nav-link ${activeKey === 'dashboard' ? 'active' : ''}"><i class="fa-solid fa-gauge"></i> Dashboard</a>
    <a href="jobs.html" class="nav-link ${activeKey === 'jobs' ? 'active' : ''}"><i class="fa-solid fa-briefcase"></i> Browse Jobs</a>
    <a href="applications.html" class="nav-link ${activeKey === 'applications' ? 'active' : ''}"><i class="fa-regular fa-bookmark"></i> My Applications</a>
    <a href="profile.html" class="nav-link ${activeKey === 'profile' ? 'active' : ''}"><i class="fa-regular fa-user"></i> Profile &amp; Resume</a>
  `;
  const adminLinks = `
    <div class="nav-section-label">Admin</div>
    <a href="admin-dashboard.html" class="nav-link ${activeKey === 'dashboard' ? 'active' : ''}"><i class="fa-solid fa-gauge"></i> Dashboard</a>
    <a href="admin-jobs.html" class="nav-link ${activeKey === 'jobs' ? 'active' : ''}"><i class="fa-solid fa-briefcase"></i> Job Postings</a>
    <a href="admin-candidates.html" class="nav-link ${activeKey === 'candidates' ? 'active' : ''}"><i class="fa-solid fa-users"></i> Candidates</a>
  `;

  mount.innerHTML = `<aside class="app-sidebar">${role === "admin" ? adminLinks : candidateLinks}</aside>`;
}


function requireRole(role) {
  if (!Auth.isLoggedIn()) { window.location.href = "login.html"; return false; }
  if (Auth.getRole() !== role) {
    window.location.href = Auth.getRole() === "admin" ? "admin-dashboard.html" : "candidate-dashboard.html";
    return false;
  }
  return true;
}

document.addEventListener("DOMContentLoaded", () => {
  // Pages opt in by setting window.__navActive before this script tag, or default ""
  renderNavbar(window.__navActive || "");
});
