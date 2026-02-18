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

// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Flatpickr
  const datePicker = flatpickr("#date-picker", {
    mode: "range",
    dateFormat: "Y-m-d",
    onClose: function (selectedDates, dateStr, instance) {
      if (selectedDates.length > 0) {
        let url = new URL(window.location.href);

        // Clear existing date parameters
        url.searchParams.delete("startdate");
        url.searchParams.delete("enddate");

        // Add start date if it exists
        if (selectedDates[0]) {
          url.searchParams.set(
            "startdate",
            selectedDates[0].toISOString().split("T")[0]
          );
        }

        // Add end date if it exists
        if (selectedDates[1]) {
          url.searchParams.set(
            "enddate",
            selectedDates[1].toISOString().split("T")[0]
          );
        }

        // Redirect to the new URL
        window.location.href = url.toString();
      }
    },
  });

  // Remove startdate and enddate parameters on page load
  (function removeDateParameters() {
    let url = new URL(window.location.href);
    if (url.searchParams.has("startdate") || url.searchParams.has("enddate")) {
      // Remove the date parameters
      url.searchParams.delete("startdate");
      url.searchParams.delete("enddate");

      // Update the URL without reloading the page
      window.history.replaceState({}, document.title, url.toString());
    }
  })();
});

document.addEventListener("DOMContentLoaded", function () {
  const categoryButton = document.getElementById("category-button");
  const categoryDropdown = document.getElementById("category-dropdown");
  console.log("Category button and dropdown are found.");

  if (categoryButton && categoryDropdown) {
    console.log("Category button and dropdown are found.");
    // Toggle dropdown when category button is clicked
    categoryButton.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevents closing dropdown on click inside it
      categoryDropdown.classList.toggle("show"); // Toggles visibility
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
      if (
        !categoryButton.contains(e.target) &&
        !categoryDropdown.contains(e.target)
      ) {
        categoryDropdown.classList.remove("show"); // Closes the dropdown
      }
    });
  }
});
