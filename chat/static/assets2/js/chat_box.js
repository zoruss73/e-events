document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const main = document.getElementById("main");
    const backToSidebar = document.getElementById("backToSidebar");
    const aboutElements = document.querySelectorAll(".rawr");

    // Function to show main chat and hide sidebar
    function showChatPage() {
        sidebar.classList.add("hidden");
        main.classList.add("visible");
        backToSidebar.classList.add("show"); // Show back button
    }

    // Click event for .about elements
    aboutElements.forEach(about => {
        about.addEventListener("click", function () {
            showChatPage();
        });
    });

    // Back to sidebar
    backToSidebar.addEventListener("click", function () {
        sidebar.classList.remove("hidden");
        main.classList.remove("visible");
        backToSidebar.classList.remove("show"); // Hide back button
    });
});