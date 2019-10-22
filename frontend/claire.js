//Define HTML Blocks and start default page
function defineStartBlock(){
    // var startBlock = '<h1> CLaire CLever - CL-Chatbot </h1>';
    var startBlock = ''
    startBlock += defineBotBlock("Hallo! Mein Name ist CLaire CLever und ich bin CL-Studentin an der UZH. Wie kann ich dir helfen?");
    return startBlock;
}

function defineBotBlock(answer){
    var botBlock = '<div class="container">'
    botBlock += '<img src="claire_avatar.png" alt="Avatar">'
    botBlock += '<p>' + answer + '</p>'
    botBlock += '<span class="time-right">' + getTime() + '</span>'
    botBlock += '</div>';
    return botBlock;
}

function defineUserBlock(question){
    var userBlock = '<div class="container darker">'
    userBlock += '<img src="user.png" alt="Avatar" class="right">'
    userBlock += '<p>' + question + '</p>'
    userBlock += '<span class="time-left">' + getTime() + '</span>'
    userBlock += '</div>';
    return userBlock;
}

function loadChatbox(){
    window.id = "To be set.";
    window.closeSession = "False";
    $("#myBox").append(defineStartBlock());
    document.getElementById("myInput").value = '';
    document.getElementById("myInput").select();
}

function newSession(){
    deleteInstance();
    setTimeout(buildNewSession, 150)
}

function buildNewSession(){
    $("#myBox").empty();
    loadChatbox();
    window.sessionClosed = "False"
}

//Functions (submit and interpret user input)
function submitInput(){
    if (window.sessionClosed == "True") {
        alert("Starte ein neues Gespräch, in dem du auf die Schaltfläche klickst.")
    } else {
        var input = getInput();
        if (input != "") {
            displayInput(input);
        }
        question = getInput();
        $.ajax({
            url: "http://127.0.0.1:5000/chatbot",
            data: {id: window.id, question: question, close_session: window.closeSession},
            dataType: "text",
            type: "POST", 
            success: function(output){
                interpretOutput(output);
            },
            error: function(error){
                console.log("Error:" + JSON.stringify(error));
            }
        });
        document.getElementById("myInput").value = '';
    }
}

function interpretOutput(output){
    var output = JSON.parse(output);
    var answer = output["answer"];
    window.id = output["id"];
    window.closeSession = output["close_session"];
    displayOutput(answer);
    console.log(answer);
    console.log(id);
    console.log(window.closeSession)
    if (window.closeSession == "True") {
        window.sessionClosed = "True"
    }
}

function deleteInstance(){
    window.closeSession = "True";
    submitInput()
}

//Utils
function getTime(){
    var today = new Date();
    var time = pad2(today.getHours()) + ":" + pad2(today.getMinutes());
    return time
}

function pad2(number){
    return (number < 10 ? '0' : '') + number
}

function getInput(){
    input = document.getElementById("myInput").value;
    return input;
}

function displayInput(){
    var input = getInput();
    $("#myBox").append(defineUserBlock(input));
    $('html, body').animate({scrollTop:$(document).height()}, 'fast')
    document.getElementById("myInput").select();
}

function displayOutput(output){
    if (output != "") {
        $("#myBox").append(defineBotBlock(output));
        $('html, body').animate({scrollTop:$(document).height()}, 'fast')
    }
}