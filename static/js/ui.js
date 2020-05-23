const API_URL = 'http://localhost:5000/api'

/*************************************** */
/** Apply tagify to keywords             */
/*************************************** */

// Global Variables
let allKeywordsInput = document.querySelectorAll("input[name=keywords]");
let allKeywordsTagify;

// Event on page load
$(document).ready(applyTagify(allKeywordsInput));

// Callback
function applyTagify(keywords) {
    // Apply tagify to each files keywords
    for (let keyword of keywords) {
        allKeywordsTagify = new Tagify(keyword, {
            dropdown: {
                position: "input"
            }
        });
    }
}

/*************************************** */
/** Set category1 & 2 default option     */
/*************************************** */
// WTForms does not have a way to set the default option
// So using JS on page load will set the default options

// Get all categories
const categories = document.querySelectorAll("select.form-control");
// Set default option values
for (let category of categories) {
    category.value = category.getAttribute('value');
}

/*************************************** */
/** Remove all tags from image           */
/*************************************** */

// Event
$("#image-list").on("click", ".tags--removeAllBtn", removeAllTags);

// Callback clears input values and removes all tags to selected file
function removeAllTags(e) {
    // Get file id
    const fileId = (e.target).closest("li").id;
    const $tags = $(`#${fileId} .${fileId}-keywords tags tag`);
    const $input = $(`#${fileId} .${fileId}-keywords input`);

    $input.value = '';
    $tags.remove();
}

/*************************************** */
/** Delete selected image                */
/*************************************** */

// Event
$("#image-list").on("click", ".delete-button", deleteImage);

// Callback sends delete request to API and remove li
async function deleteImage(e) {
    e.preventDefault();

    const imageLI = (e.target).closest("li");
    const imageId = imageLI.id;

    await axios.delete(`${API_URL}/delete/${imageId}`)
        .then(resp => console.log(resp))
        .then(() => imageLI.remove())
        .then(() => location.reload())
        .catch(err => console.log(err))
}

/*************************************** */
/** Delete  all images                   */
/*************************************** */

// Event
$("#delete-all-btn").on("click", deleteAllImages);

// Callback sends delete request to API for all images and refreshes page 
async function deleteAllImages(e) {
    e.preventDefault();

    await axios.delete((`${API_URL}/delete/all`))
        .then(resp => console.log(resp))
        .then(function () {
            location.reload()
        })
        .catch(err => console.log(err))
}

/*************************************** */
/** Delete User and user images          */
/*************************************** */

// Event
$("#delete-user").on("click", deleteUser);

// Callback sends delete request to API and remove li
async function deleteUser(e) {
    e.preventDefault();
    console.log("click...");

    // const userId = $(this).data("delete-user");

    await axios
        .all([axios.delete(`${API_URL}/delete/all`), axios.delete(`${API_URL}/users/delete`)])
        .then(axios.spread((...resp) => console.log(resp)))
        .then(() => window.location = "/signup")
        .catch(err => console.log(err))
}