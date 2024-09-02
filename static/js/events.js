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
