/**
 * JobRadar AutoPilot AI - Chrome Extension Content Script
 * Auto-detects ATS forms (Greenhouse, Lever, Workday, Ashby, iCIMS),
 * queries the local JobRadar backend API to resolve candidate fields & answers,
 * and auto-fills input fields on company career pages.
 */

console.log("[JobRadar Agent] Content script injected.");

// Detect ATS signature on the current web page
function detectATS() {
  const url = window.location.href.toLowerCase();
  const html = document.body ? document.body.innerHTML.toLowerCase() : "";

  if (url.includes("greenhouse.io") || document.getElementById("application_form") || document.getElementById("grnhse_app")) {
    return "greenhouse";
  } else if (url.includes("lever.co") || document.querySelector(".lever-application-form")) {
    return "lever";
  } else if (url.includes("myworkdayjobs.com") || document.querySelector('[data-automation-id="workday-application"]')) {
    return "workday";
  } else if (url.includes("ashbyhq.com") || document.querySelector('[data-ashby-form]')) {
    return "ashby";
  } else if (url.includes("icims.com") || document.querySelector(".iCIMS_JobsTable")) {
    return "icims";
  }
  return "generic_ats";
}

// Scrape visible inputs and their labels
function scanFormInputs() {
  const fields = [];
  const inputs = document.querySelectorAll("input, textarea, select");

  inputs.forEach((el, idx) => {
    // Skip hidden or submit buttons
    if (el.type === "hidden" || el.type === "submit" || el.type === "button") return;

    let labelText = "";
    if (el.id) {
      const labelEl = document.querySelector(`label[for="${el.id}"]`);
      if (labelEl) labelText = labelEl.innerText.trim();
    }
    if (!labelText && el.closest("label")) {
      labelText = el.closest("label").innerText.trim();
    }
    if (!labelText) {
      labelText = el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.name || `field_${idx}`;
    }

    fields.push({
      id: el.id || el.name || `idx_${idx}`,
      name: el.name || el.id || "",
      label: labelText,
      type: el.type || "text",
      tagName: el.tagName.toLowerCase()
    });
  });

  return fields;
}

// Auto-fill inputs with resolved values from JobRadar
function applyResolvedValues(resolvedMap) {
  let filledCount = 0;

  for (const [key, val] of Object.entries(resolvedMap)) {
    if (!val) continue;

    let el = document.getElementById(key) || document.querySelector(`[name="${key}"]`);
    if (!el) {
      // Try finding by label text heuristic
      const inputs = document.querySelectorAll("input, textarea, select");
      for (const inp of inputs) {
        const placeholder = inp.placeholder || "";
        const ariaLabel = inp.getAttribute("aria-label") || "";
        if (placeholder.toLowerCase().includes(key.toLowerCase()) || ariaLabel.toLowerCase().includes(key.toLowerCase())) {
          el = inp;
          break;
        }
      }
    }

    if (el) {
      if (el.tagName.toLowerCase() === "select") {
        for (let opt of el.options) {
          if (opt.text.toLowerCase().includes(val.toLowerCase()) || opt.value.toLowerCase().includes(val.toLowerCase())) {
            el.value = opt.value;
            break;
          }
        }
      } else if (el.type === "radio" || el.type === "checkbox") {
        if (val === "Yes" || val === true) el.checked = true;
      } else {
        el.value = val;
      }
      
      // Dispatch input and change events for reactive forms (React/Angular/Vue)
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      filledCount++;
    }
  }

  return filledCount;
}

// Listen for messages from extension popup
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  if (req.action === "DETECT_AND_FILL") {
    const atsType = detectATS();
    const fields = scanFormInputs();

    // Call local JobRadar backend resolver
    fetch("http://127.0.0.1:5000/api/extension/resolve_form", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ats_type: atsType,
        fields: fields,
        page_url: window.location.href,
        page_title: document.title
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.resolved_fields) {
          const count = applyResolvedValues(data.resolved_fields);
          sendResponse({
            success: true,
            atsType: atsType,
            filledCount: count,
            totalFields: fields.length
          });
        } else {
          sendResponse({ success: false, error: data.error || "Resolver error" });
        }
      })
      .catch(err => {
        sendResponse({ success: false, error: "Cannot connect to JobRadar local server (127.0.0.1:5000)" });
      });

    return true; // Keep channel open for async response
  }
});
