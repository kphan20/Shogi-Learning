// gets color of player - either 1 (black) or -1 (white)
// possible change this to simply be a string
// if so, change playerColorStr
let playerColor = parseInt(sessionStorage.getItem("color"));
// if playerColor is 0, randomize start
if (!playerColor) playerColor = Math.round(Math.random()) * 2 - 1;

let selectedPiece;
const cells = document.querySelectorAll("td");

// const pieceMap = {
//     "king": 1,
//     "gold-gen": 2,
//     "rook": 3,
//     "bishop": 4,
//     "silv-gen": 5,
//     "lance": 6,
//     "knight": 7,
//     "pawn": 8,
//     "prom-rook": 9,
//     "prom-bish": 10,
//     "prom-silv-gen": 11,
//     "prom-lance": 12,
//     "prom-knight": 13,
//     "prom-pawn": 14
// }

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

// takes in a board configuration and inits
const initBoard = (board) => {
  const htmlBoard = document.getElementById("shogi-board");
  // adds check to make sure board is valid
  board.forEach((row, rowInd) => {
    row.forEach((col, colInd) => {
      if (col) {
        // adjusts for board orientation being black-oriented
        col *= playerColor;
        htmlBoard.rows[rowInd + 1].cells[colInd].setAttribute(
          "align",
          "center"
        );
        const newPiece = document.createElement("img");
        newPiece.setAttribute(
          "src",
          "https://upload.wikimedia.org/wikipedia/commons/0/05/Shogi_osho%28svg%29.svg"
        );
        // current piece classes:
        // piece [color] [piece name]
        newPiece.setAttribute(
          "class",
          `piece ${col > 0 ? "black" : "white"} ${pieceMap[Math.abs(col)]}`
        );
        // flips opposing player's pieces
        if (col * playerColor < 0) {
          newPiece.style.transform = "scaleY(-1)";
        }
        htmlBoard.rows[rowInd + 1].cells[colInd].appendChild(newPiece);
      }
    });
  });
};
initBoard(defaultBoard);

// will send this to the backend, who will flip it in order to analyze
// the board
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
  console.log(board);
};

console.log(playerColor);
getBoard();
const pieceArr = document.querySelectorAll(".piece");
pieceArr.forEach((el) => {
  el.addEventListener("mousedown", (e) => {
    // need to change selected piece logic
    const classes = el.getAttribute("class").split(" ");
    selectedPiece = classes[PIECE_NAME];
    console.log(selectedPiece);
  });
});

cells.forEach((cell) => {
  cell.addEventListener("click", () => {
    console.log(
      `${parseInt(cell.parentElement.rowIndex) - 1}, ${cell.cellIndex}`
    );
  });
});
