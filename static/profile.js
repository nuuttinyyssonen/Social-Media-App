let editBtn = document.getElementById('edit');
let div = document.getElementById('edit-description');
let title = document.getElementById('title');
let image = document.getElementById('img');
let hiddenBtn = document.getElementById('hidden-button');

function editDescription() {
    if(div.style.display == 'none') {
        div.style.display = 'flex'
    } else {
        div.style.display = 'none'
    }
}

editBtn.addEventListener('click', editDescription)