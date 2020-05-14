// $(async function () {
const BASE_URL = 'http://localhost:5000/api'

// Use Tagify to create keywords UI
let allKeywordsInput = document.querySelectorAll("input[name=keywords");
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

// ! TODO: handle multiple images
// ? GET ALL LI ELEMENTS
// ? SEND EVERYTHING AS JSON TO SERVER
document.getElementById("csv-download").addEventListener("click", getCSV);

async function getCSV(e) {
    e.preventDefault();

    let filename = document.querySelector("form #filename").value;
    let description = document.querySelector("form #description").value;
    let category1 = document.querySelector("form #category1").value;
    let category2 = document.querySelector("form #category2").value;
    let editorial = document.querySelector("form #editorial").value;
    let r_rated = document.querySelector("form #r_rated").value;
    let location = document.querySelector("form #location").value;

    const tags = document.querySelectorAll("tag.tagify__tag");

    const keywords = getKeywords(tags);

    console.log(filename, description, category1, category2, editorial, r_rated, location);

    const resp = axios.post(`${BASE_URL}/csv`, {
        filename,
        description,
        keywords,
        category1,
        category2,
        editorial,
        r_rated,
        location
    })
    console.log(resp);
}

function getKeywords(tags) {
    // Shutterstock CSV wants keywords to be a string separated by commas
    let keywords = [];

    for (let tag of tags) {
        keywords.push(tag.textContent);
    }

    return keywords.join();
}

// ! TODO remove <hr> tag when image is deleted
// Handle Delete Image Button
$("#image-list").on("click", ".delete-button", deleteImage);
async function deleteImage(e) {
    // Send delete request to API and remove li
    e.preventDefault();

    const imageLI = (e.target).closest("li");
    const imageId = imageLI.id;
    console.log(imageId);

    await axios.delete(`${BASE_URL}/delete/${imageId}`);
    imageLI.remove();
}