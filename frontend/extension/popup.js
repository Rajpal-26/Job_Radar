document.getElementById("btnAutoFill").addEventListener("click", async () => {
  const statusBox = document.getElementById("statusBox");
  statusBox.innerHTML = "⚙️ Scanning page & resolving form...";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    statusBox.innerText = "Error: No active tab found.";
    return;
  }

  chrome.tabs.sendMessage(tab.id, { action: "DETECT_AND_FILL" }, (res) => {
    if (chrome.runtime.lastError) {
      statusBox.innerHTML = `⚠️ Error: Could not connect to page. Make sure you are on a supported job posting.`;
      return;
    }

    if (res && res.success) {
      statusBox.innerHTML = `✅ Successfully auto-filled <strong>${res.filledCount}</strong> fields on <strong>${res.atsType.toUpperCase()}</strong>!`;
    } else {
      statusBox.innerHTML = `⚠️ ${res ? res.error : "Unknown error"}`;
    }
  });
});
