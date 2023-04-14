let messageValue = document.getElementById('messageValue');
let sendBtn = document.getElementById('send');
let leaveBtn = document.getElementById('leave');
let messageArea = document.getElementById('message');
let title = document.getElementById('title');

let socket = io()

// const connection = (username) => {
//     const content = username
// }

// socket.on('connect', function(data) {
//     connection(data.username)
// })

const createMessage = (msg) => {
    let linebreak = document.createElement('br');
    let paragraph = document.createElement('p');
    paragraph.classList.add("text")
    const content = msg
    paragraph.textContent = content
    console.log(content)
    messageArea.append(paragraph)
    messageArea.append(linebreak)
}

socket.on('message', function(data) {
    createMessage(data.message)
    console.log(data.message)
})

const sendMessage = () => {
    if(messageValue == "") {
        return; 
    }
    socket.emit('message', {data: messageValue.value})
    messageValue.value = ""
}

sendBtn.addEventListener('click', sendMessage)

const leaveRoom = () => {
    socket.on('disconnect', function() {
        socket.disconnect()
    })
    window.location.href = "{{ url_for('mainpage') }}"
}

leaveBtn.addEventListener('click', leaveRoom)
