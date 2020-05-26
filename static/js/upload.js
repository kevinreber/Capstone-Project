// ###############################################################
//     Dropzone  ------------------------------------------------#
// ###############################################################

// "myAwesomeDropzone" is the camelized version of the HTML element's ID
Dropzone.options.uploadForm = {
    // uploadMultiple: true,
    acceptedFiles: "image/*",
    addRemoveLinkes: true,
    maxFilesize: 10, // MB
    init: function () {
        this.on("success", function (file, resp) {
            console.log(file, resp);
        })
    }
};

/**************************************** */
/** Remove all tags from preview and DB   */
/**************************************** */

// Event
$("#delete-uploaded-images").on("click", deleteAllImagesFromUploads);

// Removes all images from form preview and DB
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