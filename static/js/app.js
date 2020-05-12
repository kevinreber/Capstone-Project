const BASE_URL = 'http://localhost:5000/api'

// Use Tagify to create keywords UI
const keywords = document.querySelector("input[name=keywords");

const keywordsTagify = new Tagify(keywords, {
    dropdown: {
        position: "input"
    }
});

// "remove all tags" button event listener
document.querySelector('.tags--removeAllBtn')
    .addEventListener('click', keywordsTagify.removeAllTags.bind(keywordsTagify));

const downloadCSV = document.getElementById("csv-download");

downloadCSV.addEventListener("click", getCSV);

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