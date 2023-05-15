let upload = document.getElementById('upload')
let uploadBtn = document.getElementById('uploadBtn')

function uploadImg() {
    if (upload.style.display == 'none') {
        upload.style.display = "flex"
    } else {
        upload.style.display = "none"
    }
}
        
uploadBtn.addEventListener('click', uploadImg)