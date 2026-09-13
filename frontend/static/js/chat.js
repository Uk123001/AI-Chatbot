(() => {
  const API_BASE = ""; // same-origin; set to a full URL if frontend is hosted separately

  const chatLog = document.getElementById("chat-log");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const statusLine = document.getElementById("status-line");
  const pdfInput = document.getElementById("pdf-input");
  const uploadLabel = document.getElementById("upload-label");
  const docList = document.getElementById("doc-list");

  function getSessionId() {
    let id = localStorage.getItem("aster_session_id");
    if (!id) {
      id = "sess_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem("aster_session_id", id);
    }
    return id;
  }
  const sessionId = getSessionId();

  function appendMessage(role, text) {
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    wrap.appendChild(bubble);
    chatLog.appendChild(wrap);
    chatLog.scrollTop = chatLog.scrollHeight;
    return wrap;
  }

  function setStatus(text) {
    if (!text) {
      statusLine.hidden = true;
      statusLine.textContent = "";
      return;
    }
    statusLine.hidden = false;
    statusLine.textContent = text;
  }

  async function sendMessage(message) {
    appendMessage("user", message);
    sendBtn.disabled = true;
    const thinking = appendMessage("bot", "…");

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message }),
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        thinking.querySelector(".bubble").textContent =
          errBody.detail || "Something went wrong. Please try again.";
        return;
      }

      const data = await res.json();
      thinking.querySelector(".bubble").textContent = data.reply;

      if (data.stage === "booked" && data.booking_id) {
        setStatus(`✓ Booking #${data.booking_id} saved`);
      } else if (data.stage === "confirming") {
        setStatus("Awaiting your confirmation…");
      } else if (data.stage === "collecting") {
        setStatus("Collecting booking details…");
      } else {
        setStatus("");
      }
    } catch (err) {
      thinking.querySelector(".bubble").textContent =
        "Couldn't reach the server. Please check your connection and try again.";
    } finally {
      sendBtn.disabled = false;
      chatInput.focus();
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    chatInput.value = "";
    sendMessage(message);
  });

  pdfInput.addEventListener("change", async () => {
    const file = pdfInput.files[0];
    if (!file) return;

    uploadLabel.textContent = `Uploading ${file.name}…`;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: formData });
      const data = await res.json();

      if (!res.ok) {
        uploadLabel.textContent = data.detail || "Upload failed. Try another PDF.";
        return;
      }

      uploadLabel.textContent = "Choose a PDF or drag it here";
      const li = document.createElement("li");
      li.textContent = `${data.filename} — ${data.chunks_indexed} chunks indexed`;
      docList.appendChild(li);
      appendMessage("system", data.message);
    } catch (err) {
      uploadLabel.textContent = "Upload failed. Try again.";
    }
  });
})();
