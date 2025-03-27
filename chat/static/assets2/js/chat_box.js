document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const main = document.getElementById("main");
    const backToSidebar = document.getElementById("backToSidebar");

    function toggleView() {
        const currentPath = window.location.pathname;

        if (currentPath === "/message/") {
            // Show only sidebar when the URL is exactly /message/
            sidebar?.classList.remove("hidden");
            main?.classList.remove("visible");
            main?.classList.add("hidden");
            backToSidebar?.classList.add("d-none"); // Hide back button
        } else if (currentPath.startsWith("/message/c/")) {
            // Show only the chat when a room is selected
            sidebar?.classList.add("hidden");
            main?.classList.add("visible");
            main?.classList.remove("hidden");
            backToSidebar?.classList.remove("d-none"); // Show back button
        } else {
            // Default behavior for larger screens
            sidebar?.classList.remove("hidden");
            main?.classList.add("visible");
            main?.classList.remove("hidden");
            backToSidebar?.classList.add("d-none"); // Hide back button
        }
    }

    // Ensure back button exists before adding event listener
    if (backToSidebar) {
        backToSidebar.addEventListener("click", function () {
            window.location.href = "/message/"; // Navigate back to /message/
        });
    }

    // Initially call the function to set the correct view
    toggleView();

    // Listen for navigation changes
    window.addEventListener("popstate", toggleView);
});
