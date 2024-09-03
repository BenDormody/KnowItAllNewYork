document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll("tr[data-event-id]");
  const detailsDiv = document.getElementById("event-details");

  rows.forEach((row) => {
    row.addEventListener("mouseenter", () => {
      const eventId = row.getAttribute("data-event-id");
      fetchEventDetails(eventId);
    });
  });

  function fetchEventDetails(eventId) {
    detailsDiv.innerHTML = "Loading...";

    fetch(`/api/event/${eventId}`)
      .then((response) => response.json())
      .then((event) => {
        detailsDiv.innerHTML = `
                    <h2>${event.description}</h2>
                    <p><strong>Date:</strong> ${new Date(
                      event.date
                    ).toLocaleString()}</p>
                    <p><strong>Description:</strong> ${event.description}</p>
                    <p><strong>Tag:</strong> ${event.tag}</p>
                `;
      })
      .catch((error) => {
        console.error("Error:", error);
        detailsDiv.innerHTML = "Error loading event details.";
      });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const tableContainer = document.querySelector(".table-container");
  const stickyHeader = document.getElementById("sticky-header");
  const dateHeaders = document.querySelectorAll(".date-header");

  function updateStickyHeader() {
    let currentDate = null;
    const containerRect = tableContainer.getBoundingClientRect();
    const containerTop = containerRect.top;

    for (let header of dateHeaders) {
      const headerRect = header.getBoundingClientRect();
      if (headerRect.top <= containerTop) {
        currentDate = header.dataset.date;
      } else {
        break;
      }
    }

    if (currentDate) {
      stickyHeader.textContent = currentDate;
      stickyHeader.style.display = "block";
    } else {
      stickyHeader.style.display = "none";
    }
  }

  tableContainer.addEventListener("scroll", updateStickyHeader);
  window.addEventListener("scroll", updateStickyHeader);
  window.addEventListener("resize", updateStickyHeader);

  // Initial call to set correct state on page load
  updateStickyHeader();
});
