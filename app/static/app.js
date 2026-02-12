const processForm = document.getElementById("process-form");
const replayForm = document.getElementById("replay-form");
const processResult = document.getElementById("process-result");
const replayResult = document.getElementById("replay-result");
const failuresBody = document.getElementById("failures-body");
const refreshBtn = document.getElementById("refresh-btn");

function showResult(el, payload) {
  el.textContent = JSON.stringify(payload, null, 2);
}

async function fetchFailures() {
  try {
    const response = await fetch("/failures");
    const data = await response.json();

    if (!Array.isArray(data) || data.length === 0) {
      failuresBody.innerHTML = '<tr><td colspan="5" class="empty">No records yet.</td></tr>';
      return;
    }

    failuresBody.innerHTML = data
      .map((item) => {
        const statusClass = item.status === "FAILED" ? "status-failed" : "status-success";
        return `
          <tr>
            <td>${item.id}</td>
            <td class="${statusClass}">${item.status}</td>
            <td>${item.retry_count}</td>
            <td>${item.idempotency_key ?? "-"}</td>
            <td>${item.error_message ?? "-"}</td>
          </tr>
        `;
      })
      .join("");
  } catch (error) {
    failuresBody.innerHTML = '<tr><td colspan="5" class="empty">Failed to load data.</td></tr>';
  }
}

processForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const idempotencyKey = document.getElementById("idempotency_key").value.trim();
  const fail = document.getElementById("fail").checked;

  const payload = { fail };
  if (idempotencyKey) {
    payload.idempotency_key = idempotencyKey;
  }

  try {
    const response = await fetch("/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    showResult(processResult, await response.json());
    await fetchFailures();
  } catch (error) {
    showResult(processResult, { message: "Request failed", error: String(error) });
  }
});

replayForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const requestId = document.getElementById("request_id").value;

  try {
    const response = await fetch(`/replay/${requestId}`, { method: "POST" });
    showResult(replayResult, await response.json());
    await fetchFailures();
  } catch (error) {
    showResult(replayResult, { message: "Replay failed", error: String(error) });
  }
});

refreshBtn.addEventListener("click", fetchFailures);
fetchFailures();
