// ! TODO: handle multiple images
// ? SEND EVERYTHING AS JSON TO SERVER

$("#image-list").on("submit", getCSV);

async function getCSV(e) {
    e.preventDefault();

    const images = document.querySelectorAll("#image-list .image-container");
    let csv = "Filename, Description, Keywords, Categories, Editorial,R-Rated, Location\n";

    console.log("start...");

    for (let image of images) {
        csv += getFileIdData(image.id).join(",");
        csv += "\n";
    }

    console.log(csv);

    console.log("end...");

    // const jsonData = JSON.stringify(data);
    // console.log(jsonData);

    downloadCSV(csv, "testing.csv");

    // await axios.post(`${API_URL}/csv`, {
    //         "data": data
    //     })
    //     .then(resp => console.log(resp))
    //     .catch(err => console.log(err))
}


function downloadCSV(csv, filename) {
    console.log("downloading....");

    let csvFile;
    let downloadLink;

    // CSV file
    csvFile = new Blob([csv], {
        type: "text/csv"
    });

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);
    // Hide download link
    downloadLink.style.display = "none";
    // Add the link to DOM
    document.body.appendChild(downloadLink);

    // Click download link
    downloadLink.click();
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

    // const obj = {
    //     fileId,
    //     filename,
    //     description,
    //     categories,
    //     editorial,
    //     r_rated,
    //     location,
    //     keywords
    // };

    const arr = [
        filename,
        description,
        keywords,
        categories,
        editorial,
        r_rated,
        location
    ];

    console.log(arr);

    return arr;
}

function parseKeywords(tags) {
    // CSV needs keywords to be a string separated by commas
    let keywords = '';

    for (let [index, tag] of tags.entries()) {
        if (index !== tags.length - 1) {
            keywords += `${tag.textContent},`;
        } else keywords += tag.textContent;
    }

    return keywords;
}