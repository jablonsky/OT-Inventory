document.addEventListener("DOMContentLoaded", () => {
    const exportButton = document.querySelector("[data-export-csv]");
    const exportStatus = document.querySelector("#csv-export-status");
    const exportStatusMessage = document.querySelector("#csv-export-status-message");
    const exportStatusClose = document.querySelector("[data-export-status-close]");

    if (!exportButton || !exportStatus || !exportStatusMessage || !exportStatusClose) {
        return;
    }

    const showStatus = (message, category) => {
        exportStatus.className = `alert alert-${category} alert-dismissible mb-4`;
        exportStatusMessage.textContent = message;
    };

    exportStatusClose.addEventListener("click", () => {
        exportStatus.classList.add("d-none");
    });

    const responseFilename = (response) => {
        const disposition = response.headers.get("Content-Disposition") || "";
        const match = disposition.match(/filename="?([^";]+)"?/i);
        return match ? match[1] : "ot-inventory.csv";
    };

    exportButton.addEventListener("click", async (event) => {
        event.preventDefault();

        if (exportButton.getAttribute("aria-disabled") === "true") {
            return;
        }

        const originalContent = exportButton.innerHTML;
        exportButton.classList.add("disabled");
        exportButton.setAttribute("aria-disabled", "true");
        exportButton.innerHTML = [
            '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>',
            "Preparing CSV…",
        ].join("");
        showStatus("Extracting inventory data and preparing the CSV file…", "info");

        try {
            const response = await fetch(exportButton.href, {
                credentials: "same-origin",
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });
            const contentType = response.headers.get("Content-Type") || "";

            if (!response.ok || !contentType.includes("text/csv")) {
                throw new Error("The server did not return a CSV file.");
            }

            const csvBlob = await response.blob();
            const downloadUrl = URL.createObjectURL(csvBlob);
            const downloadLink = document.createElement("a");

            downloadLink.href = downloadUrl;
            downloadLink.download = responseFilename(response);
            document.body.appendChild(downloadLink);
            downloadLink.click();
            downloadLink.remove();
            window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);

            showStatus("CSV download started successfully.", "success");
        } catch (error) {
            showStatus("The CSV export could not be created. Please try again.", "danger");
        } finally {
            exportButton.classList.remove("disabled");
            exportButton.removeAttribute("aria-disabled");
            exportButton.innerHTML = originalContent;
        }
    });
});
