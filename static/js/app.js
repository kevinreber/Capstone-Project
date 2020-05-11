// Use Tagify for keywords UI
const keywords = document.querySelector("input[name=keywords");

const keywordsTagify = new Tagify(keywords, {
    dropdown: {
        position: "input"
    }
});

// "remove all tags" button event listener
document.querySelector('.tags--removeAllBtn')
    .addEventListener('click', keywordsTagify.removeAllTags.bind(keywordsTagify));