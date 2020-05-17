const API_URL = 'http://localhost:5000/api'

// Use Tagify to create keywords UI
let allKeywordsInput = document.querySelectorAll("input[name=keywords]");
let allKeywordsTagify;

$(document).ready(applyTagify(allKeywordsInput));

function applyTagify(keywords) {

    for (let keyword of keywords) {
        allKeywordsTagify = new Tagify(keyword, {
            dropdown: {
                position: "input"
            }
        });
    }
}

// ! TODO: fix "remove all tags"
// "remove all tags" button event listener
// document.querySelectorAll('.tags--removeAllBtn')
//     .addEventListener('click', keywordsTagify.removeAllTags.bind(keywordsTagify));

// ! TODO remove <hr> tag when image is deleted
// Handle Delete Image Button
$("#image-list").on("click", ".delete-button", deleteImage);
async function deleteImage(e) {
    // Send delete request to API and remove li
    e.preventDefault();

    const imageLI = (e.target).closest("li");
    const imageId = imageLI.id;
    console.log(imageId);

    await axios.delete(`${API_URL}/delete/${imageId}`)
        .then(resp => console.log(resp))
        .catch(err => console.log(err))
    imageLI.remove();
}