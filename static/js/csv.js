// ! TODO: handle multiple images
// ? SEND EVERYTHING AS JSON TO SERVER

$("#image-list").on("submit", getCSV);

async function getCSV(e) {
    e.preventDefault();

    // const $lis = $("#image-list .image-container");
    const images = document.querySelectorAll("#image-list .image-container");
    let data = {};

    console.log("start...");

    for (let image of images) {
        data[image.id] = getFileIdData(image.id);
    }
    console.log(data);

    console.log("end...");

    const jsonData = JSON.stringify(data);
    console.log(jsonData);

    // await axios.post(`${API_URL}/csv`, {
    //         "data": data
    //     })
    //     .then(resp => console.log(resp))
    //     .catch(err => console.log(err))
}





/***************************** */
/** Handle form data for CSV */
/***************************** */
function getFileIdData(fileId) {
    // get file container by fileId
    const file = document.getElementById(fileId);

    const filename = file.querySelector("input[name=filename]").value;
    const description = file.querySelector("input[name=description]").value;
    const category1 = file.querySelector("select[name=category1]").value;
    const category2 = file.querySelector("select[name=category2]").value;
    const editorial = file.querySelector("input[name=editorial]").value;
    const r_rated = file.querySelector("input[name=r_rated]").value;
    const location = file.querySelector("input[name=location]").value;

    const tags = file.querySelectorAll('.tagify__tag');
    const keywords = parseKeywords(tags);

    // Parse categories together
    const categories = [category1, category2].join(",")

    const obj = {
        fileId,
        filename,
        description,
        categories,
        editorial,
        r_rated,
        location,
        keywords
    };

    return obj;
}

function parseKeywords(tags) {
    // CSV needs keywords to be a string separated by commas
    let keywords = [];

    for (let tag of tags) {
        keywords.push(tag.textContent);
    }

    return keywords.join();
}