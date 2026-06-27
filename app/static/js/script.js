const startBtn = document.getElementById("startBtn");
const summaryBox = document.getElementById("summaryOutput");
const summaryContent = document.getElementById("summaryContent");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");

startBtn.addEventListener("click", async () => {
  startBtn.disabled = true;
  loading.classList.remove("hidden");
  errorBox.classList.add("hidden");
  summaryBox.classList.add("hidden");

  try {
    const res = await fetch("/summarize");
    const data = await res.json();

    loading.classList.add("hidden");

    if (data && data.summary) {
      summaryContent.innerText = data.summary;
      summaryBox.classList.remove("hidden");
    } else {
      throw new Error("Empty response");
    }
  } catch (err) {
    loading.classList.add("hidden");
    errorBox.classList.remove("hidden");
  }

  startBtn.disabled = false;
});


document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById("startBtn");
  const summaryBox = document.getElementById("summaryOutput");
  const summaryContent = document.getElementById("summaryContent");
  const loading = document.getElementById("loading");
  const errorBox = document.getElementById("errorBox");

  startBtn.addEventListener("click", async () => {
      startBtn.disabled = true;
      loading.classList.remove("hidden");
      errorBox.classList.add("hidden");
      summaryBox.classList.add("hidden");

      try {
          const res = await fetch("/summarize");
          const data = await res.json();

          loading.classList.add("hidden");

          if (data && data.summary) {
              summaryContent.innerText = data.summary;
              summaryBox.classList.remove("hidden");
          } else {
              throw new Error("Empty response");
          }
      } catch (err) {
          loading.classList.add("hidden");
          errorBox.classList.remove("hidden");
      }

      startBtn.disabled = false;
  });
});