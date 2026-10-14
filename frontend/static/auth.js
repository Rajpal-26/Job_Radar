/**
 * WATERMARK: Rajpal Singh Tanwar
 * Copyright (c) 2026 Rajpal Singh Tanwar. All rights reserved.
 * JobRadar In-App Auth, Employee Onboarding & Multi-Tenancy Engine
 */

let currentAuthUser = null;
let currentAuthModalTab = "signup";
let pendingAuthCallback = null;
let pendingActionTitle = null;

// ==============================================================================
// AUTH GATE FUNCTION (Enforces Employee Registration/Login on Dashboard Actions)
// ==============================================================================

/**
 * Gatekeeper function: If user is authenticated, executes callback immediately.
 * If not authenticated, opens the Employee Registration Modal, saves the callback,
 * and automatically triggers it as soon as the employee registers or logs in.
 */
window.requireAuthOrRegister = function(callback, actionTitle = "Dashboard Action") {
  if (currentAuthUser && currentAuthUser.email) {
    if (typeof callback === "function") {
      callback();
    }
    return true;
  }

  // Save pending callback
  pendingAuthCallback = callback;
  pendingActionTitle = actionTitle;

  // Open modal in Register / Onboarding mode
  openAuthModal("signup", actionTitle);
  return false;
};

// ==============================================================================
// AUTH STATE CHECK & NAVBAR RENDERING
// ==============================================================================

async function checkAuthState() {
  try {
    const res = await fetch("/api/auth/me");
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated && data.user) {
        currentAuthUser = data.user;
        renderNavUserWidget(data.user);
        return data.user;
      }
    }
  } catch (e) {
    console.debug("Auth check status: unauthenticated", e);
  }
  currentAuthUser = null;
  renderNavLoggedOutWidget();
  return null;
}

function renderNavUserWidget(user) {
  const navTools = document.querySelector(".nav-tools") || document.querySelector(".nav-brand")?.parentElement;
  if (!navTools) return;

  let userWidget = document.getElementById("jobradarNavUserWidget");
  if (!userWidget) {
    userWidget = document.createElement("div");
    userWidget.id = "jobradarNavUserWidget";
    userWidget.style.cssText = "display: inline-flex; align-items: center; gap: 0.75rem; margin-left: 0.5rem; position: relative;";
    navTools.appendChild(userWidget);
  }

  const credits = user.credit_balance !== undefined ? user.credit_balance : 10;
  const initials = (user.full_name || user.email || "EM").slice(0, 2).toUpperCase();

  userWidget.innerHTML = `
    <!-- Credit Wallet Badge -->
    <div title="Available AI Search & Auto-Apply Credits" style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.4rem 0.85rem; border-radius: 999px; background: var(--accent-soft); border: 1px solid var(--accent); color: var(--accent); font-weight: 800; font-size: 0.84rem; user-select: none;">
      <span style="font-size: 0.95rem;">⚡</span>
      <span id="navCreditCount">${credits} Credits</span>
    </div>

    <!-- User Avatar & Dropdown Trigger -->
    <div style="position: relative;">
      <button type="button" id="userMenuBtn" onclick="toggleUserDropdown(event)" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.3rem 0.65rem 0.3rem 0.35rem; border-radius: 999px; background: var(--panel-soft); border: 1px solid var(--line); color: var(--text); cursor: pointer; font-weight: 700; font-size: 0.85rem; transition: all 0.2s ease;">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%); color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.75rem;">
          ${initials}
        </div>
        <span style="max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(user.full_name || user.email)}</span>
        <span style="font-size: 0.65rem; color: var(--subtext);">▼</span>
      </button>

      <!-- Dropdown Menu -->
      <div id="userDropdownMenu" style="display: none; position: absolute; right: 0; top: 115%; width: 250px; background: var(--panel); border: 1px solid var(--line); border-radius: 0.75rem; box-shadow: var(--shadow); padding: 0.5rem; z-index: 2000;">
        <div style="padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--line); margin-bottom: 0.35rem;">
          <div style="font-weight: 800; font-size: 0.88rem; color: var(--text);">${escapeHtml(user.full_name || 'Employee / Candidate')}</div>
          <div style="font-size: 0.75rem; color: var(--subtext); overflow: hidden; text-overflow: ellipsis;">${escapeHtml(user.email)}</div>
          <div style="margin-top: 0.35rem; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.7rem; font-weight: 800; padding: 0.15rem 0.45rem; border-radius: 4px; background: var(--primary-soft); color: var(--primary);">
              ${(user.plan || 'Free').toUpperCase()} PLAN
            </span>
            <span style="font-size: 0.72rem; color: var(--accent); font-weight: 700;">⚡ ${credits} Credits</span>
          </div>
        </div>

        <a href="/" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.65rem; border-radius: 0.4rem; color: var(--text); text-decoration: none; font-size: 0.84rem; font-weight: 600;" onmouseover="this.style.background='var(--panel-soft)'" onmouseout="this.style.background='transparent'">
          ⚡ Multi-Portal Dashboard
        </a>
        <a href="/auto-apply" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.65rem; border-radius: 0.4rem; color: var(--text); text-decoration: none; font-size: 0.84rem; font-weight: 600;" onmouseover="this.style.background='var(--panel-soft)'" onmouseout="this.style.background='transparent'">
          🚀 Auto Apply Studio
        </a>
        <a href="/tracker" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.65rem; border-radius: 0.4rem; color: var(--text); text-decoration: none; font-size: 0.84rem; font-weight: 600;" onmouseover="this.style.background='var(--panel-soft)'" onmouseout="this.style.background='transparent'">
          📌 Kanban Tracker
        </a>
        <a href="/recruiters" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.65rem; border-radius: 0.4rem; color: var(--text); text-decoration: none; font-size: 0.84rem; font-weight: 600;" onmouseover="this.style.background='var(--panel-soft)'" onmouseout="this.style.background='transparent'">
          🎯 Recruiter Radar
        </a>

        <div style="border-top: 1px solid var(--line); margin: 0.35rem 0;"></div>

        <button type="button" onclick="jobradarInAppLogout()" style="width: 100%; text-align: left; display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.65rem; border-radius: 0.4rem; color: var(--error); background: transparent; border: none; font-size: 0.84rem; font-weight: 700; cursor: pointer;" onmouseover="this.style.background='rgba(239, 110, 117, 0.12)'" onmouseout="this.style.background='transparent'">
          🚪 Sign Out
        </button>
      </div>
    </div>
  `;
}

function renderNavLoggedOutWidget() {
  const navTools = document.querySelector(".nav-tools") || document.querySelector(".nav-brand")?.parentElement;
  if (!navTools) return;

  let userWidget = document.getElementById("jobradarNavUserWidget");
  if (!userWidget) {
    userWidget = document.createElement("div");
    userWidget.id = "jobradarNavUserWidget";
    userWidget.style.cssText = "display: inline-flex; align-items: center; gap: 0.6rem; margin-left: 0.5rem;";
    navTools.appendChild(userWidget);
  }

  userWidget.innerHTML = `
    <button type="button" onclick="openAuthModal('signin')" style="padding: 0.45rem 1rem; border-radius: 0.65rem; border: 1px solid var(--line); background: var(--panel-soft); color: var(--text); font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: all 0.2s ease;">
      Sign In
    </button>
    <button type="button" onclick="openAuthModal('signup')" class="cove-btn-primary" style="padding: 0.45rem 1.15rem; border-radius: 0.65rem; font-weight: 800; font-size: 0.85rem;">
      Register Employee &bull; Free
    </button>
  `;
}

function toggleUserDropdown(e) {
  e.stopPropagation();
  const menu = document.getElementById("userDropdownMenu");
  if (menu) {
    menu.style.display = menu.style.display === "block" ? "none" : "block";
  }
}

document.addEventListener("click", () => {
  const menu = document.getElementById("userDropdownMenu");
  if (menu) menu.style.display = "none";
});

// ==============================================================================
// IN-APP LOGOUT
// ==============================================================================

async function jobradarInAppLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch (e) {}
  localStorage.removeItem("jobradar_user");
  currentAuthUser = null;
  renderNavLoggedOutWidget();
  showToast("Logged out successfully.", "info");
}

// ==============================================================================
// IN-APP AUTH MODAL (Register, Sign In, 1-Click Social, Instant Employee Setup)
// ==============================================================================

function injectAuthModalDOM() {
  if (document.getElementById("jobradarAuthModal")) return;

  const modal = document.createElement("div");
  modal.id = "jobradarAuthModal";
  modal.className = "modal";

  modal.innerHTML = `
    <div class="modal-content" style="max-width: 480px; position: relative;">
      
      <!-- Close Button -->
      <button type="button" onclick="closeAuthModal()" style="position: absolute; right: 1.25rem; top: 1.25rem; background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--subtext); line-height: 1;">&times;</button>

      <!-- Modal Header -->
      <div style="text-align: center; margin-bottom: 1.25rem;">
        <div style="display: inline-flex; align-items: center; gap: 0.5rem; font-size: 1.5rem; font-weight: 800; margin-bottom: 0.25rem; color: var(--text);">
          <div style="width: 10px; height: 10px; background: var(--accent); border-radius: 50%; box-shadow: 0 0 10px var(--accent);"></div>
          Job<span style="color: var(--primary);">Radar</span>
        </div>
        <div id="modalActionSubtitle" style="font-size: 0.88rem; color: var(--subtext); margin-top: 0.2rem;">
          Register your employee profile to unlock AI search &amp; auto apply
        </div>
      </div>

      <!-- Action Prompt Banner (when triggered by a dashboard button) -->
      <div id="modalActionGateBanner" style="display: none; background: var(--primary-soft); border: 1px solid var(--primary); padding: 0.6rem 0.85rem; border-radius: 0.65rem; margin-bottom: 1rem; font-size: 0.84rem; color: var(--text); text-align: center;">
        ⚡ Complete quick registration to automatically execute: <strong id="modalActionGateName" style="color: var(--primary);">Search</strong>
      </div>

      <!-- Free Credits Banner -->
      <div style="display: flex; align-items: center; gap: 0.6rem; background: var(--accent-soft); border: 1px solid var(--accent); padding: 0.55rem 0.9rem; border-radius: 0.65rem; margin-bottom: 1.25rem; font-size: 0.84rem; font-weight: 600; color: var(--text);">
        <span style="font-size: 1.2rem;">🎁</span>
        <div><strong style="color: var(--accent);">10 Free Credits</strong> granted instantly upon registration for AI job scraping &amp; auto apply.</div>
      </div>

      <!-- 1-Click Fast Instant Employee Registration -->
      <div id="modalQuickRegisterBox" style="margin-bottom: 1rem;">
        <button type="button" onclick="handleQuickEmployeeOnboarding()" class="cove-btn-accent" style="width: 100%;">
          <span>⚡ 1-Click Instant Employee Onboarding</span>
        </button>
        <div style="text-align: center; font-size: 0.75rem; color: var(--subtext); margin-top: 0.35rem;">
          Instant registration with 10 credits &bull; Zero configuration required
        </div>
      </div>

      <!-- Alert Box inside Modal -->
      <div id="modalAlertBox" style="display: none; padding: 0.6rem 0.85rem; border-radius: 0.5rem; font-size: 0.82rem; font-weight: 600; margin-bottom: 1rem; text-align: center;"></div>

      <!-- Tabs -->
      <div style="display: flex; background: var(--panel-soft); border: 1px solid var(--line); border-radius: 0.65rem; padding: 0.25rem; gap: 0.25rem; margin-bottom: 1.25rem;">
        <button type="button" id="modalTabSignUp" onclick="switchModalAuthTab('signup')" style="flex: 1; padding: 0.5rem; border-radius: 0.45rem; font-size: 0.82rem; font-weight: 700; border: none; cursor: pointer; background: var(--panel); color: var(--primary); box-shadow: 0 2px 6px rgba(0,0,0,0.1);">Register Employee</button>
        <button type="button" id="modalTabSignIn" onclick="switchModalAuthTab('signin')" style="flex: 1; padding: 0.5rem; border-radius: 0.45rem; font-size: 0.82rem; font-weight: 700; border: none; cursor: pointer; background: transparent; color: var(--subtext);">Sign In</button>
        <button type="button" id="modalTabMagic" onclick="switchModalAuthTab('magic')" style="flex: 1; padding: 0.5rem; border-radius: 0.45rem; font-size: 0.82rem; font-weight: 700; border: none; cursor: pointer; background: transparent; color: var(--subtext);">Magic Link</button>
      </div>

      <!-- 1-Click Social Sign-In / Register -->
      <div id="modalSocialButtons" style="display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1rem;">
        <button type="button" onclick="handleInAppSocialLogin('google')" class="btn-soft" style="width: 100%; justify-content: center;">
          <svg style="width: 18px; height: 18px;" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
          </svg>
          <span id="modalGoogleBtnText">Continue with Google</span>
        </button>

        <button type="button" onclick="handleInAppSocialLogin('github')" class="btn-soft" style="width: 100%; justify-content: center;">
          <svg style="width: 18px; height: 18px;" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
          <span id="modalGithubBtnText">Continue with GitHub</span>
        </button>
      </div>

      <div id="modalDivider" style="display: flex; align-items: center; text-align: center; margin: 1rem 0; color: var(--subtext); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">
        <span style="flex: 1; border-bottom: 1px solid var(--line); margin-right: .5em;"></span>
        <span>or with credentials</span>
        <span style="flex: 1; border-bottom: 1px solid var(--line); margin-left: .5em;"></span>
      </div>

      <!-- Form -->
      <form id="modalAuthForm" onsubmit="handleModalAuthSubmit(event)">
        <div id="modalNameField" style="display: block; margin-bottom: 0.85rem;">
          <label style="display: block; font-size: 0.82rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem;">Employee / Full Name</label>
          <input type="text" id="modalInputName" class="input-field" placeholder="e.g. Alex Mercer" />
        </div>

        <div style="margin-bottom: 0.85rem;">
          <label style="display: block; font-size: 0.82rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem;">Email Address</label>
          <input type="email" id="modalInputEmail" required class="input-field" placeholder="employee@company.com" />
        </div>

        <div id="modalPasswordField" style="margin-bottom: 1.15rem;">
          <label style="display: block; font-size: 0.82rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem;">Password</label>
          <input type="password" id="modalInputPassword" class="input-field" placeholder="••••••••••••" />
        </div>

        <button type="submit" id="modalSubmitBtn" class="cove-btn-primary" style="width: 100%;">
          <span id="modalSubmitBtnText">Register Employee &amp; Get 10 Credits</span>
        </button>
      </form>
    </div>
  `;

  document.body.appendChild(modal);
}

function openAuthModal(mode = "signup", actionTitle = null) {
  injectAuthModalDOM();
  const modal = document.getElementById("jobradarAuthModal");
  if (!modal) return;

  const gateBanner = document.getElementById("modalActionGateBanner");
  const gateName = document.getElementById("modalActionGateName");
  if (actionTitle && gateBanner && gateName) {
    gateBanner.style.display = "block";
    gateName.textContent = actionTitle;
  } else if (gateBanner) {
    gateBanner.style.display = "none";
  }

  modal.style.display = "flex";
  switchModalAuthTab(mode);
}

function closeAuthModal() {
  const modal = document.getElementById("jobradarAuthModal");
  if (modal) modal.style.display = "none";
}

function switchModalAuthTab(mode) {
  currentAuthModalTab = mode;
  const alertBox = document.getElementById("modalAlertBox");
  if (alertBox) alertBox.style.display = "none";

  const btnSignIn = document.getElementById("modalTabSignIn");
  const btnSignUp = document.getElementById("modalTabSignUp");
  const btnMagic = document.getElementById("modalTabMagic");
  const nameField = document.getElementById("modalNameField");
  const pwdField = document.getElementById("modalPasswordField");
  const socialGroup = document.getElementById("modalSocialButtons");
  const divider = document.getElementById("modalDivider");
  const submitText = document.getElementById("modalSubmitBtnText");
  const quickBox = document.getElementById("modalQuickRegisterBox");

  [btnSignIn, btnSignUp, btnMagic].forEach(b => {
    if (b) {
      b.style.background = "transparent";
      b.style.color = "var(--subtext)";
      b.style.boxShadow = "none";
    }
  });

  if (mode === "signin") {
    if (btnSignIn) {
      btnSignIn.style.background = "var(--panel)";
      btnSignIn.style.color = "var(--primary)";
      btnSignIn.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";
    }
    if (nameField) nameField.style.display = "none";
    if (pwdField) pwdField.style.display = "block";
    if (socialGroup) socialGroup.style.display = "flex";
    if (divider) divider.style.display = "flex";
    if (quickBox) quickBox.style.display = "none";
    if (submitText) submitText.textContent = "Sign In & Access Dashboard";
  } else if (mode === "signup") {
    if (btnSignUp) {
      btnSignUp.style.background = "var(--panel)";
      btnSignUp.style.color = "var(--primary)";
      btnSignUp.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";
    }
    if (nameField) nameField.style.display = "block";
    if (pwdField) pwdField.style.display = "block";
    if (socialGroup) socialGroup.style.display = "flex";
    if (divider) divider.style.display = "flex";
    if (quickBox) quickBox.style.display = "block";
    if (submitText) submitText.textContent = "Register Employee & Claim 10 Credits";
  } else if (mode === "magic") {
    if (btnMagic) {
      btnMagic.style.background = "var(--panel)";
      btnMagic.style.color = "var(--primary)";
      btnMagic.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";
    }
    if (nameField) nameField.style.display = "none";
    if (pwdField) pwdField.style.display = "none";
    if (socialGroup) socialGroup.style.display = "none";
    if (divider) divider.style.display = "none";
    if (quickBox) quickBox.style.display = "none";
    if (submitText) submitText.textContent = "Send 15-Min Magic Link ✨";
  }
}

function showModalAlert(msg, isError = true) {
  const box = document.getElementById("modalAlertBox");
  if (!box) return;
  box.textContent = msg;
  box.style.background = isError ? "rgba(239, 110, 117, 0.15)" : "rgba(47, 178, 130, 0.15)";
  box.style.border = isError ? "1px solid var(--error, #ef6e75)" : "1px solid var(--success, #2fb282)";
  box.style.color = isError ? "var(--error, #ef6e75)" : "var(--success, #2fb282)";
  box.style.display = "block";
}

// 1-Click Fast Instant Employee Onboarding
async function handleQuickEmployeeOnboarding() {
  showModalAlert("Provisioning instant employee account with 10 credits...", false);
  try {
    const res = await fetch("/api/auth/quick-register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: "Demo Candidate" })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      onAuthSuccess(data.user, "🎉 Employee registered successfully! 10 Welcome Credits activated.");
    } else {
      showModalAlert(data.error || "Instant registration failed. Please try email registration.");
    }
  } catch (err) {
    showModalAlert("Network error during instant onboarding.");
  }
}

async function handleModalAuthSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("modalInputEmail").value.trim();
  const password = document.getElementById("modalInputPassword").value;
  const fullName = document.getElementById("modalInputName").value.trim();
  const btn = document.getElementById("modalSubmitBtn");
  const btnText = document.getElementById("modalSubmitBtnText");

  if (!email) {
    showModalAlert("Please provide your email address.");
    return;
  }

  btn.disabled = true;
  btnText.textContent = currentAuthModalTab === "signup" ? "Registering Employee..." : "Authenticating...";

  try {
    let endpoint = "/api/auth/login";
    let payload = { email, password };

    if (currentAuthModalTab === "signup") {
      endpoint = "/api/auth/register";
      payload = { email, password, full_name: fullName };
    } else if (currentAuthModalTab === "magic") {
      endpoint = "/api/auth/magic-link";
      payload = { email };
    }

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      showModalAlert(data.error || "Authentication failed.");
      btn.disabled = false;
      switchModalAuthTab(currentAuthModalTab);
      return;
    }

    if (currentAuthModalTab === "magic") {
      showModalAlert("✨ Magic Link dispatched to your inbox!", false);
      btn.disabled = false;
      return;
    }

    // Successful login/signup
    const welcomeMsg = currentAuthModalTab === "signup"
      ? `🎉 Welcome ${data.user?.full_name || 'Candidate'}! 10 Welcome Credits activated.`
      : `Welcome back, ${data.user?.full_name || 'Candidate'}!`;
    
    onAuthSuccess(data.user, welcomeMsg);

  } catch (err) {
    showModalAlert("Network error. Please try again.");
    btn.disabled = false;
    switchModalAuthTab(currentAuthModalTab);
  }
}

async function handleInAppSocialLogin(provider) {
  showModalAlert(`Connecting to ${provider.toUpperCase()} 1-Click Login...`, false);
  try {
    const res = await fetch("/api/auth/social-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider })
    });
    const data = await res.json();
    if (data.success) {
      onAuthSuccess(data.user, `🎉 Signed in via ${provider}! 10 Free Credits ready.`);
    } else {
      showModalAlert(data.error || "Social sign-in failed.");
    }
  } catch (e) {
    showModalAlert("Error connecting to OAuth gateway.");
  }
}

/**
 * Handle successful authentication: update state, render navbar, close modal,
 * and seamlessly execute any pending user action (e.g. search).
 */
function onAuthSuccess(user, toastMessage) {
  currentAuthUser = user;
  renderNavUserWidget(user);
  closeAuthModal();
  showToast(toastMessage || `Welcome ${user?.full_name || 'Candidate'}!`, "success");

  // If the user clicked a dashboard action before registering/logging in, trigger it now!
  if (typeof pendingAuthCallback === "function") {
    const callbackToRun = pendingAuthCallback;
    pendingAuthCallback = null;
    pendingActionTitle = null;
    setTimeout(() => {
      callbackToRun();
    }, 200);
  }
}

function showToast(msg, type = "info") {
  let toast = document.getElementById("jobradarAppToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "jobradarAppToast";
    toast.style.cssText = "position: fixed; bottom: 1.5rem; right: 1.5rem; padding: 0.75rem 1.25rem; border-radius: 0.75rem; z-index: 10000; font-weight: 700; font-size: 0.88rem; box-shadow: var(--shadow, 0 8px 24px rgba(0,0,0,0.4)); transition: all 0.3s ease; display: none;";
    document.body.appendChild(toast);
  }

  if (type === "success") {
    toast.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
    toast.style.color = "#ffffff";
    toast.style.border = "none";
  } else {
    toast.style.background = "var(--panel, #090d16)";
    toast.style.border = "1px solid var(--line, #21314a)";
    toast.style.color = "var(--text, #e7edf8)";
  }

  toast.textContent = msg;
  toast.style.display = "block";
  toast.style.opacity = "1";

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => { toast.style.display = "none"; }, 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Auto-run on page load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", checkAuthState);
} else {
  checkAuthState();
}
