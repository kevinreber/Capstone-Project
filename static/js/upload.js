// ###############################################################
//     Dropzone  ------------------------------------------------#
// ###############################################################

// "myAwesomeDropzone" is the camelized version of the HTML element's ID
Dropzone.options.uploadForm = {
    // paramName: "file", // The name that will be used to transfer the file
    // method: "POST",
    // uploadMultiple: true,
    acceptedFiles: "image/*",
    addRemoveLinkes: true,
    // maxFilesize: 2, // MB
    // accept: function (file, done) {
    //     if (file.name == "justinbieber.jpg") {
    //         done("Naha, you don't.");
    //     } else {
    //         done();
    //     }
    // },
    init: function () {
        this.on("success", function (file, resp) {
            console.log(file, resp);
        })
    }
};

$("#delete-uploaded-images").on("click", deleteAllImagesFromUploads);

async function deleteAllImagesFromUploads(e) {
    e.preventDefault();
    $previews = $("#upload-form .dz-preview");

    await axios.delete((`${API_URL}/delete/all`))
        .then(resp => console.log(resp))
        .then(function () {
            for (let preview of $previews) {
                preview.remove();
            }
        }).then(function () {
            $("#upload-form .dz-default.dz-message").show();
        })
        .catch(err => console.log(err))
}