document.addEventListener("DOMContentLoaded", function () {
    // Project Image Preview
    const projectImgInput = document.querySelector("#id_img"); // Adjust ID if necessary
    const projectImgPreview = document.querySelector("#imgPreview");

    if (projectImgInput) {
        projectImgInput.addEventListener("change", function () {
            previewImage(this, projectImgPreview);
        });
    }

    // Award Image Preview
    const awardImgInput = document.querySelector("#id_award_img"); // Ensure correct ID
    const awardImgPreview = document.querySelector("#awardImgPreview");

    if (awardImgInput) {
        awardImgInput.addEventListener("change", function () {
            previewImage(this, awardImgPreview);
        });
    }

    // Function to preview image
    function previewImage(input, previewElement) {
        const file = input.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewElement.src = e.target.result;
                previewElement.classList.remove("d-none"); // Show image preview
            };
            reader.readAsDataURL(file);
        } else {
            previewElement.src = "";
            previewElement.classList.add("d-none"); // Hide preview if no image
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // Loop through all the award forms
    const awardForms = document.querySelectorAll('[id^="form_update_award_"]');

    awardForms.forEach(form => {
        const awardId = form.id.split('_').pop(); // Get the award ID from the form ID

        // Award Image Input and Image tag elements
        const awardImgInput = form.querySelector(`#img${awardId}`);
        const awardImgTag = form.querySelector(`#awardImgPreview`);

        if (awardImgInput) {
            awardImgInput.addEventListener("change", function () {
                updateImagePreview(this, awardImgTag);
            });
        }

        // Function to update image preview in the image tag
        function updateImagePreview(input, imgTag) {
            const file = input.files[0];

            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imgTag.src = e.target.result; // Update the src of the image tag with the new image
                    imgTag.classList.remove("d-none"); // Ensure the image is visible
                };
                reader.readAsDataURL(file);
            }
        }
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            Swal.fire({
                title: "Please wait...",
                text: "",
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        });
    }
});


const confirmDelete = (awardId) => {
    Swal.fire({
        title: "Confirm Delete",
        icon: "question",
        text: "Are you sure to delete this award? This action cannot be undone.",
        // showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: "Delete",
        confirmButtonColor: '#dc3545',
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/organizer/system-settings/delete-awards/${awardId}/`
        }
    });
}

const confirmDeleteService = (serviceId) => {
    Swal.fire({
        title: "Confirm Delete",
        icon: "question",
        text: "Are you sure to delete this service? This action cannot be undone.",
        // showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: "Delete",
        confirmButtonColor: '#dc3545',
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/organizer/delete-service/${serviceId}/`
        }
    });
}

const confirmDeleteFaq = (faqId) => {
    Swal.fire({
        title: "Confirm Delete",
        icon: "question",
        text: "Are you sure to delete this faq? This action cannot be undone.",
        showCancelButton: true,
        confirmButtonText: "Delete",
        confirmButtonColor: '#dc3545',
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/organizer/delete-faq/${faqId}/`
        }
    });
}

const confirmMarkAsComplete = (bookingId) => {
    Swal.fire({
        title: "Confirm Update",
        icon: "question",
        text: "Are you sure to mark this event as complete? This action cannot be undone.",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        confirmButtonColor: '#198754',
        cancelButtonColor: '#dc3545',
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/organizer/bookings/${bookingId}/`
        }
    });
}


const searchInput = document.getElementById('searchInput');
const cards = document.querySelectorAll('.info-card');
const noResultsMessage = document.getElementById('no-results');

if (searchInput) {
    searchInput.addEventListener('input', function () {
        const query = this.value.toLowerCase();
        let resultsFound = false;

        cards.forEach(card => {
            const name = card.getAttribute('data-name').toLowerCase();
            if (name.includes(query)) {
                card.parentElement.style.display = 'block';
                resultsFound = true;
            } else {
                card.parentElement.style.display = 'none';
            }
        });

        if (resultsFound) {
            noResultsMessage.classList.add('d-none');
        } else {
            noResultsMessage.classList.remove('d-none');
        }
    });
}

document.getElementById('searchBookingInput').addEventListener('keyup', function() {
    var searchValue = this.value.toLowerCase();
    var cards = document.querySelectorAll('.info-card');
    var noResult = document.querySelector('.no-result');
    var anyVisible = false;

    cards.forEach(function(card) {
        var cardText = card.innerText.toLowerCase();
        if (cardText.includes(searchValue)) {
            card.parentElement.style.display = 'block';
            anyVisible = true;
        } else {
            card.parentElement.style.display = 'none'; 
        }
    });

    if (anyVisible) {
        noResult.classList.add('d-none'); 
    } else {
        noResult.classList.remove('d-none');
    }
});



