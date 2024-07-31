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

function sortTable(columnIndex) {
  var table = document.getElementById("sortableTable");
  var rows = Array.prototype.slice.call(table.querySelectorAll("tbody > tr"));

  rows.sort(function (rowA, rowB) {
    var cellA = rowA.cells[columnIndex].textContent;
    var cellB = rowB.cells[columnIndex].textContent;

    if (!isNaN(cellA) && !isNaN(cellB)) {
      return cellA - cellB;
    }

    return cellA.localeCompare(cellB);
  });

  rows.forEach(function (row) {
    table.querySelector("tbody").appendChild(row);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("titleHeader").addEventListener("click", function () {
    sortTable(0);
  });
  document
    .getElementById("descriptionHeader")
    .addEventListener("click", function () {
      sortTable(1);
    });
  document.getElementById("dateHeader").addEventListener("click", function () {
    sortTable(2);
  });
});
