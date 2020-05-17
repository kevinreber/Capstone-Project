// ************************ Drag and drop ***************** //
let dropArea = document.getElementById('drop-area');
let progressBar = document.getElementById('progress-bar')
let uploadProgress = []
// let filesDone = 0
// let filesToDo = 0

// ###############################################################
//     UPLOAD HELPER FUNCTIONS   --------------------------------#
// ###############################################################

function preventDefaults(e) {
    e.preventDefault()
    e.stopPropagation()
}

function highlight(e) {
    dropArea.classList.add('highlight')
}

function unhighlight(e) {
    dropArea.classList.remove('active')
}

function handleDrop(e) {
    let dt = e.dataTransfer
    let files = dt.files

    handleFiles(files)
}

function handleFiles(files) {
    files = [...files]
    initializeProgress(files.length)
    files.forEach(uploadFile)
    files.forEach(previewFile)
}

// ###############################################################
//     UPLOAD EVENT HANDLERS   ----------------------------------#
// ###############################################################

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false)
    document.body.addEventListener(eventName, preventDefaults, false)
});

// Toggle highlight drop area when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false)
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false)
});

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false);

// ###############################################################
//     Progress Bars   ------------------------------------------#
// ###############################################################
function initializeProgress(numFiles) {
    progressBar.value = 0
    uploadProgress = []

    for (let i = numFiles; i > 0; i--) {
        uploadProgress.push(0)
    }
}

function updateProgress(fileNumber, percent) {
    uploadProgress[fileNumber] = percent
    let total = uploadProgress.reduce((tot, curr) => tot + curr, 0) / uploadProgress.length
    console.debug('update', fileNumber, percent, total)
    progressBar.value = total
}

function previewFile(file) {
    let reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onloadend = function () {
        let img = document.createElement('img')
        img.src = reader.result
        document.getElementById('gallery').appendChild(img)
    }
}

// ###############################################################
//     Submit Form   --------------------------------------------#
// ###############################################################
function uploadFile(file, i) {
    console.log('uploading....');

    var url = '/api/upload'
    var xhr = new XMLHttpRequest()
    var formData = new FormData()
    xhr.open('POST', url, true)
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')

    // Show update progress 
    xhr.upload.addEventListener("progress", function (e) {
        updateProgress(i, (e.loaded * 100.0 / e.total) || 100)
    })

    xhr.addEventListener('readystatechange', function (e) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            updateProgress(i, 100)
        } else if (xhr.readyState == 4 && xhr.status != 200) {
            console.log(e, 'error');
        }
    })

    formData.append('file', file)
    xhr.send(formData)
}