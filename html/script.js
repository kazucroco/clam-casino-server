//rough pseudocode:
//prompt on loading page for server ip
//new game button: send POST to ip
//receive game id
//(NOT YET IMPLEMENTED:) receive 
//when user clicks a card:
//send POST request with card info
//receive response
//flip card based on response

const servInput = document.getElementById("servername");
const form = document.getElementById("serverForm");
form.addEventListener("submit", function(event) {
    event.preventDefault();
    const serverID=servInput.value;
    const pushAddress=serverID+"/new";//user should only enter address not port or /new
    console.log(serverID);
    const gamecode = fetchReq(pushAddress).then(value=>connectMain(value, serverID).then(totals=>initBoard(totals)));
});
//begin junji code
    const allCards = document.querySelectorAll(".card");
    const restartBtn = document.getElementById("btn-restart");
    const restartGameBtn = document.getElementById("btn-restart-game");
    const gameOverScreen = document.getElementById("game-over-screen");
    const currentScore = document.getElementById("current-score");

    function initBoard(totals) {
      let rowScores = [0, 0, 0, 0, 0, 0];
      let rowBombs = [0, 0, 0, 0, 0, 0];
      let colScores = [0, 0, 0, 0, 0, 0];
      let colBombs = [0, 0, 0, 0, 0, 0];

      allCards.forEach((card) => {
        card.classList.remove(
          "is-flipped",
          "val-0",
          "val-1",
          "val-2",
          "val-3",
        );

        //const val = Math.floor(Math.random() * 4);
        //card.setAttribute("data-val", val);

        const r = parseInt(card.getAttribute("data-row"));
        const c = parseInt(card.getAttribute("data-col"));
      });

      for (let i = 0; i < 6; i++) {
        document.getElementById("hint-row-" + i + "-score").innerText =
          totals.rows[i][0];//scores for row
        document.getElementById("hint-row-" + i + "-bombs").innerText =
          totals.rows[i][1];//bombs for row
        document.getElementById("hint-col-" + i + "-score").innerText =
          totals.cols[i][0];
        document.getElementById("hint-col-" + i + "-bombs").innerText =
          totals.cols[i][1];
      }
    }

    //initBoard();

    allCards.forEach((card) => {
      card.addEventListener("click", function () {
        if (!this.classList.contains("is-flipped")) {
            
            const val = flipCard(this.r, this.c, address, gamecode);//maybe add a .then
            this.classList.add("is-flipped", "val-" + val);//to make these 2 lines work
        }
      });
    });

    document.body.addEventListener(
      "click",
      function () {
        const bgm = document.getElementById("bgm");
        if (bgm.paused) {
          bgm.play();
        }
      },
      { once: true },
    );

    function resetGameUI() {
      gameOverScreen.style.display = "none";
      currentScore.innerText = "0";
      initBoard();
    }

    restartBtn.addEventListener("click", resetGameUI);
    restartGameBtn.addEventListener("click", resetGameUI);
    //end junji code
async function connectMain(gamecode, address) {//executes after address form is submitted
    //send get request for rows/cols
    //parse that info
    //display the board accordingly
    tempAddress = address + "/totals/" + gamecode;
    console.log(tempAddress);
    const rowCol=await fetchReq(tempAddress, null, "GET");
    return JSON.parse(rowCol);
}

async function flipCard(rowNum, colNum, address, gamecode) {
    tempAddress = address + "/flip/" + gamecode;
    const card = {row:rowNum.toString(), 
        col: colNum.toString()};
    console.log(JSON.stringify(card));
    const response = await fetchReq(tempAddress, card);
    return response;
}

async function fetchReq(address, jsonToUse=null, requestType="POST") {
    //need to distinguish between get and post bc get 
    //cannot have a body
    let data, response;
    if(requestType=="GET") {
        response = await fetch(address,{
        method:requestType,
        })
    }
    else {
        response = await fetch(address,{
        method:requestType,
        headers: {
        "Content-Type": "application/json"
    },
        body: JSON.stringify(jsonToUse)
        })
        
    }
    data = await response.text();
    console.log(data);
    return data;
}
