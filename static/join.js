$( document ).ready(function() {
    document.getElementById("username").focus();
    document.getElementById("username").select();
    console.log("test");
});
function signIn(){
    username = document.getElementById("username").value;
    //if username is not null
    if(username){
        window.location.replace("snek?username="+ username);
    }
    else{
        alert("You must tell us your name to play!");
    }

};
