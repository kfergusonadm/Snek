var id;
var username;



$( document ).ready(function() {

    //This variable is to scale the size of the given the client.
    //The game map is still 100x100 units, but is blown up in the UI.

    scale = 8;

    //Game colors
    regColors = ["green","red","blue"];
    colorBlind = ["#117733","#882255","#88CCEE"];
    colors = regColors;

    //user information
    id = Math.floor(Math.random() * 1000000000);
    username = $("#username").text();
    direction = "right";
    score = 0;
    console.log("id: " + id);
    console.log("username: " + username);

    //pre create json messages for the server
    left = createJsonString(id,"left");
    up = createJsonString(id,"up");
    right = createJsonString(id,"right");
    down = createJsonString(id,"down");


    //scale slider
    //slider = document.getElementById("myRange");
    //scaleVal = document.getElementById("scaleVal");
    gameWrapper = document.getElementById("gameWrapper");

    //listeners
    //color blindness checkbox
    $('input[name=colorBlind]').change(function(){
     if($(this).is(':checked')) {
            colors = colorBlind;
        } else {
            colors = regColors;
        }
    });


    //Slider listener
    //slider.oninput = function() {
     //   scale = this.value;
     //   scaleVal.value = this.value;
     //   gameWrapper.style.height = 100*scale;
     //   gameWrapper.style.width = 100*scale;
    //}

    var ws = new WebSocket("ws://localhost:8888/snekSocket/?id=" + id + "&" + "username=" + username);

    //add key event listeners
    document.addEventListener('keydown', function(event) {

        console.log("current direction: " + direction)
        //left arrow
        if (event.keyCode == 37) {
            //if facing left or right
            if(direction == "left"||direction == "right"){
                //do nothing
            }
            else{
                console.log("turn left")
                ws.send(left);
                //console.log(JSON.parse(test));
            }

        }
        //up arrow
        else if (event.keyCode == 38) {
            //if facing up or down
            if(direction == "up"||direction == "down"){
                //do nothing
            }
            else{
                ws.send(up);
                console.log("turn up")
                //console.log(JSON.parse(test));
            }
        }
        //right arrow
        else if (event.keyCode == 39) {
            //if facing left or right
            if(direction == "left"||direction == "right"){
                //do nothing
            }
            else{
                ws.send(right);
                console.log("turn right")
                //console.log(JSON.parse(test));
            }

        }
        //down arrow
        else if (event.keyCode == 40) {
            if(direction == "up"||direction == "down"){
                //do nothing
            }
            else{
                ws.send(down);
                console.log("turn down")
                //console.log(JSON.parse(test));
            }
        }
    }, true);



    //start the Game Area
    gameArea.start();

    ws.onopen = function() {
       // ws.send("Hello, world");
       // use this to send a stringified json object that looks like
       //
       // send this when player presses key to change direction
    };

    ws.onmessage = function (evt) {
       var obj = JSON.parse(evt.data);

       if ('lost' in obj){ // Player lost
            console.log(obj);
            console.log('you lost');
            alert(obj.message);
            window.location.replace("snek?username="+ username);
            // open modal saying they lost?
       }
       else {
            console.log(obj);
            direction = obj['players'][id]['direction'];
            score = obj['players'][id]['score'];
            console.log(score);
            document.getElementById("score").innerHTML = score;
            updateGameArea(obj);
       }
    };


});

//The game area canvas
var gameArea = {
    canvas : document.createElement("canvas"),
    start : function(){
        this.canvas.width = 100*scale;
        this.canvas.height = 100*scale;
        this.context = this.canvas.getContext("2d");
        document.getElementById('gameWrapper').appendChild(this.canvas);
        //this.interval = setInterval(updateGameArea, 20)
    },
    clear : function (){
        this.context.clearRect(0,0,this.canvas.width,this.canvas.height)
    }
}

updateGameArea = function(obj){
    gameArea.clear();
    handleGameObject(obj);
}

handleGameObject = function(world){

    var players = world.players;
    var food = world.food;

    var playersArray = $.map(players, function(value, index) {
        return [value];
    });
    //go through all the players
    playersArray.forEach(function(id){
        //console.log(id);
        var segments = id.segments;
        var usernameCurrent = id.username;

        segments.forEach(function(segment){
            //get coordinates of the segment
            var x = segment.x;
            var y = segment.y;

            //draw the segment
            if(username == usernameCurrent){
                createObject(colors[0],x,y);
            }
            else{
                createObject(colors[1],x,y);
            }

        });
    });
    food.forEach(function(piece){
        //get coordinates of the segment
        var x = piece.x;
        var y = piece.y;

        //draw the segment
        createObject(colors[2],x,y);
    });
};

createObject = function(color,x,y){

    ctx = gameArea.context;
    //console.log(x,y);
    ctx.fillStyle = color;
    ctx.fillRect(x*scale,y*scale,scale,scale);

};
createJsonString = function(id,direction){
    var message = new Object();
    message.id = id;
    message.username = username;
    message.direction = direction;
    var jsonString = JSON.stringify(message);
    return jsonString;
}

