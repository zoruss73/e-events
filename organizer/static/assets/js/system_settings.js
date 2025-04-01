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
