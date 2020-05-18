$("#image-list").on("submit", getCSV);

async function getCSV(e) {
    e.preventDefault();
    const images = document.querySelectorAll("#image-list .image-container");
    let data = {}

    for (let image of images) {
        data[image.id] = getFileIdData(image.id, "csv");
    }

    const jsonData = JSON.stringify(data);
    console.log(jsonData);
    await axios.post(`${API_URL}/csv`, {
            jsonData
        })
        .then(resp => console.log(resp))
        .catch(err => console.log(err))
}

$("#save-files-btn").on("click", saveFileData);

async function saveFileData(e) {
    console.log('Saving...');

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
        .catch(err => console.log(err))
}

/*************************** */
/** Handle form data for CSV */
/*************************** */
function getFileIdData(fileId, handle) {
    // get file container by fileId
    const file = document.getElementById(fileId);
    let obj = {};

    const filename = file.querySelector("input[name=filename]").value;
    const description = file.querySelector("input[name=description]").value;
    const category1 = file.querySelector("select[name=category1]").value;
    const category2 = file.querySelector("select[name=category2]").value;
    const editorialValue = file.querySelector("input[name=editorial]").value;
    const r_ratedValue = file.querySelector("input[name=r_rated]").value;
    const location = file.querySelector("input[name=location]").value;

    const tags = file.querySelectorAll('.tagify__tag');
    const keywords = parseKeywords(tags);

    if (handle === 'csv') {
        // Convert Boolean values
        const editorial = editorialValue === 'y' ? 'yes' : 'no';
        const r_rated = r_ratedValue === 'y' ? 'yes' : 'no';

        // Parse categories together
        const categories = [category1, category2].join(",")

        obj = {
            fileId,
            filename,
            description,
            categories,
            editorial,
            r_rated,
            location,
            keywords
        }
    }
    if (handle === 'save') {
        // Convert Boolean values
        const editorial = editorialValue === 'y' ? true : false;
        const r_rated = r_ratedValue === 'y' ? true : false;

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
    }
    return obj;
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