// matches piece mapping in backend
const pieceMap = [
  "empty",
  "king",
  "gold-gen",
  "rook",
  "bishop",
  "silv-gen",
  "lance",
  "knight",
  "pawn",
  "prom-rook",
  "prom-bish",
  "prom-silv-gen",
  "prom-lance",
  "prom-knight",
  "prom-pawn",
];

const pieceArt = {
  king: "https://upload.wikimedia.org/wikipedia/commons/b/bd/Shogi_gyokusho%28svg%29.svg",
  "gold-gen":
    "https://upload.wikimedia.org/wikipedia/commons/b/b1/Shogi_kinsho%28svg%29.svg",
  rook: "https://upload.wikimedia.org/wikipedia/commons/4/43/Shogi_hisha%28svg%29.svg",
  bishop:
    "https://upload.wikimedia.org/wikipedia/commons/4/4f/Shogi_kakugyo%28svg%29.svg",
  "silv-gen":
    "https://upload.wikimedia.org/wikipedia/commons/1/18/Shogi_ginsho%28svg%29.svg",
  lance:
    "https://upload.wikimedia.org/wikipedia/commons/7/77/Shogi_kyosha%28svg%29.svg",
  knight:
    "https://upload.wikimedia.org/wikipedia/commons/f/fb/Shogi_keima%28svg%29.svg",
  pawn: "https://upload.wikimedia.org/wikipedia/commons/2/2f/Shogi_fuhyo%28svg%29.svg",
  "prom-rook":
    "https://upload.wikimedia.org/wikipedia/commons/b/b5/Shogi_ryuo%28svg%29.svg",
  "prom-bish":
    "https://upload.wikimedia.org/wikipedia/commons/7/74/Shogi_ryuma%28svg%29.svg",
  "prom-silv-gen":
    "https://upload.wikimedia.org/wikipedia/commons/a/ad/Shogi_narigin%28svg%29.svg",
  "prom-lance":
    "https://upload.wikimedia.org/wikipedia/commons/f/f1/Shogi_narikyo%28svg%29.svg",
  "prom-knight":
    "https://upload.wikimedia.org/wikipedia/commons/6/65/Shogi_narikei%28svg%29.svg",
  "prom-pawn":
    "https://upload.wikimedia.org/wikipedia/commons/7/78/Shogi_tokin%28svg%29.svg",
};

// assuming this is from the perspective of the black(first) player
const defaultBoard = [
  [-6, -7, -5, -2, -1, -2, -5, -7, -6],
  [0, -3, 0, 0, 0, 0, 0, -4, 0],
  [-8, -8, -8, -8, -8, -8, -8, -8, -8],
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  [8, 8, 8, 8, 8, 8, 8, 8, 8],
  [0, 4, 0, 0, 0, 0, 0, 3, 0],
  [6, 7, 5, 2, 1, 2, 5, 7, 6],
];

// indices of piece class info
const PIECE_COLOR = 1;
const PIECE_NAME = 2;

// gets color of player - either 1 (black) or -1 (white)
let playerColor = parseInt(sessionStorage.getItem("color"));
// if playerColor is 0, randomize start
if (!playerColor) playerColor = Math.round(Math.random()) * 2 - 1;

// contains string representation of player color
const playerColorStr = playerColor === 1 ? "black" : "white";

// contains coordinates of piece that is currently selected by player
let selectedPiece;

// DOM elements stored for future interaction
const htmlBoard = document.getElementById("shogi-board");
const cells = document.querySelectorAll("td");

// takes in a board configuration and adds pieces to htmlBoard
const initBoard = (board) => {
  // adds check to make sure board is valid
  board.forEach((row, rowInd) => {
    row.forEach((col, colInd) => {
      if (col) {
        // adjusts for board orientation being black-oriented
        col *= playerColor;

        // currently using img elements to represent pieces
        const newPiece = document.createElement("img");
        const pieceName = pieceMap[Math.abs(col)];
        newPiece.setAttribute("src", pieceArt[pieceName]);
        newPiece.setAttribute("align", "middle");
        newPiece.setAttribute(
          "class",
          `piece ${col > 0 ? "black" : "white"} ${pieceName}`
        );

        // flips opposing player's pieces
        if (col * playerColor < 0) {
          newPiece.style.transform = "scaleY(-1)";
        }

        // finally appends to DOM
        htmlBoard.rows[rowInd + 1].cells[colInd].appendChild(newPiece);
      }
    });
  });
};

// for now, initialize board to standard shogi setup
initBoard(defaultBoard);

// returns 2D array of board representation for backend functions
const getBoard = () => {
  const board = Array(9)
    .fill()
    .map(() => Array(9).fill(0));
  cells.forEach((cell) => {
    if (cell.childElementCount > 0) {
      const pieceInfo = cell.firstElementChild.getAttribute("class").split(" ");
      const pieceColor = pieceInfo[PIECE_COLOR] === "black" ? 1 : -1;
      board[parseInt(cell.parentElement.rowIndex) - 1][cell.cellIndex] =
        pieceColor * pieceMap.indexOf(pieceInfo[PIECE_NAME]);
    }
  });
  return board;
};

// gets all the pieces on the board
const pieceArr = document.querySelectorAll(".piece");

// updates selected piece if player clicks on their own piece
// potentially change so that only player's piece get this listener
pieceArr.forEach((el) => {
  el.addEventListener("mousedown", () => {
    if (el.classList.contains(playerColorStr)) {
      selectedPiece = [
        parseInt(el.parentElement.parentElement.rowIndex),
        parseInt(el.parentElement.cellIndex),
      ];
    }
    console.log(selectedPiece);
  });
});

// moves selected piece if conditions are met
cells.forEach((cell) => {
  cell.setAttribute("align", "center");
  cell.addEventListener("click", () => {
    if (!cell.classList.contains("move-dest")) return;

    // if move-dest, then execute move
    if (cell.firstChild) {
      // add logic to add captured piece to player hand
      cell.firstChild.remove();
    }
    console.log(selectedPiece);
    cell.appendChild(
      htmlBoard.rows[selectedPiece[0]].cells[selectedPiece[1]].firstChild
    );
  });
});

// clears marked destination squares
const clearDestCells = () => {
  document.querySelectorAll(".move-dest").forEach((el) => {
    el.classList.remove("move-dest");
  });
};

htmlBoard.addEventListener("click", clearDestCells);
