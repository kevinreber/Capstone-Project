// Use Tagify for keywords UI
const keywords = document.querySelector("input[name=keywords");

const keywordsTagify = new Tagify(keywords, {
    dropdown: {
        position: "input"
    }
});