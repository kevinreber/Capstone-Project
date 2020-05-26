$("#image-list").on("submit", getCSV);
$("#save-files-btn").on("click", saveFileData);

/*************************** */
/** Handle saving form data  */
/*************************** */

async function saveFileData(e) {
    e.preventDefault();
    const images = document.querySelectorAll("#image-list .image-container");
    let data = {}

    for (let image of images) {
        data[image.id] = getFileIdData(image.id, "save");
    }

    const jsonData = JSON.stringify(data);
    console.log(jsonData);
    await axios.patch(`${API_URL}/update`, {
            jsonData
        })
        .then(resp => console.log(resp))
        .then(() => location.reload())
        .catch(err => console.log(err))
}

/*************************** */
/** Handle form data for CSV */
/*************************** */

// Prepare CSV string
function getCSV(e) {
    e.preventDefault();
    const images = document.querySelectorAll("#image-list .image-container");

    let csv = `Filename, Description, Keywords, Categories, Editorial, R-rated, Location\n`;

    for (let image of images) {
        csv += getFileIdData(image.id, "csv")
    }

    downloadCSV(csv);
}

// Creates Blob to download data as a CSV
function downloadCSV(data) {
    const csvBlob = new Blob([data], {
        type: "text/csv"
    });
    const blobUrl = URL.createObjectURL(csvBlob);
    const anchorElement = document.createElement("a");

    anchorElement.href = blobUrl;
    anchorElement.download = "shutterstock-images.csv";
    anchorElement.click();

    setTimeout(() => {
        URL.revokeObjectURL(blobUrl);
    }, 500);
}

/************************** */
/** Get data from form      */
/************************** */

function getFileIdData(fileId, handle) {
    // get file container by fileId
    const file = document.getElementById(fileId);
    let obj = {};

    const filename = file.querySelector("input[name=filename]").value;
    const description = file.querySelector("input[name=description]").value;
    const category1 = file.querySelector("select[name=category1]").value;
    const category2 = file.querySelector("select[name=category2]").value;
    const editorialValue = file.querySelector("input[name=editorial]");
    const r_ratedValue = file.querySelector("input[name=r_rated]");
    const location = file.querySelector("input[name=location]").value;

    const tags = file.querySelectorAll('.tagify__tag');
    const keywords = parseKeywords(tags);

    if (handle === 'csv') {
        // Convert Boolean values
        const editorial = editorialValue.checked === true ? 'yes' : 'no';
        const r_rated = r_ratedValue.checked === true ? 'yes' : 'no';

        // Parse categories together
        const categories = category2 ? [category1, category2].join(",") : category1;

        // Instead of using Pandas, build row with JS
        const row = `"${filename}", "${description}", "${keywords}", "${categories}", ${editorial}, ${r_rated}, "${location}"\n`;

        return row;
    }
    if (handle === 'save') {
        // Convert Boolean values
        const editorial = editorialValue.checked;
        const r_rated = r_ratedValue.checked;

        obj = {
            fileId,
            filename,
            description,
            category1,
            category2,
            editorial,
            r_rated,
            location,
            keywords
        }
        return obj;
    }
}

function parseKeywords(tags) {
    // CSV needs keywords to be a string separated by commas
    let keywords = [];

    for (let tag of tags) {
        keywords.push(tag.textContent);
    }

    // Join keywords together to make string
    return keywords.join();
}