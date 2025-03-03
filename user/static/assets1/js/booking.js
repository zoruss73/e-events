document.getElementById('id_wedding_date').addEventListener("change", function() {
    let wedding_date = new Date(this.value);
    let current_date = new Date();

    wedding_date.setHours(0,0,0,0)
    current_date.setHours(0,0,0,0)

    if(wedding_date < current_date ){
        Swal.fire({
            icon:"error",
            title: "Invalid date",
            text: "You cannot select past date!"
        });

        this.value = "";
    }

    else if (wedding_date.getTime() === current_date.getTime()){
        Swal.fire({
            icon:"error",
            title: "Invalid date",
            text: "You cannot book a date that is today."
        });
        
        this.value = "";

    }
});
