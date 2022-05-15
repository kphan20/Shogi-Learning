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

// current links for piece images
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
// if captured piece is selected, rank is -1 and file is piece type
let selectedPiece;

// contains the player to move
let currentPlayer = 1;

const initCapturedPieces = () => {
  const players = [-1, 1];
  const capPieces = {};
  players.forEach((player) => {
    capPieces[player] = {};
    for (let i = 2; i <= 8; i++) capPieces[player][i] = 0;
  });
  return capPieces;
};
// stores the captured pieces of each player
/* 
  Structure - 
  {
    [playerColor]:
    {
      [pieceId]: [count]
    }
  }
*/
const capturedPieces = initCapturedPieces();

// DOM elements stored for future interaction
const htmlBoard = document.getElementById("shogi-board");
const cells = document.querySelectorAll("#shogi-board td");

// given a signed piece (indicating owner and piece id), return html element
const createPiece = (piece) => {
  // currently using img elements to represent pieces
  const newPiece = document.createElement("img");
  const pieceName = pieceMap[Math.abs(piece)];
  newPiece.setAttribute("src", pieceArt[pieceName]);
  newPiece.setAttribute("align", "middle");
  newPiece.setAttribute(
    "class",
    `piece ${piece > 0 ? "black" : "white"} ${pieceName}`
  );

  // flips opposing player's pieces
  if (piece * playerColor < 0) {
    newPiece.style.transform = "scaleY(-1)";
  }

  return newPiece;
};

// taking a board configuration, adds pieces to htmlBoard and sets up
// captured pieces
const initBoard = (board) => {
  // add check to make sure board is valid

  board.forEach((row, rowInd) => {
    row.forEach((col, colInd) => {
      if (col) {
        // adjusts for board orientation being black-oriented
        // this is only accurate for symmetrical boards - like starting board
        // need to implement rotate method to be position agnostic
        col *= playerColor;
        htmlBoard.rows[rowInd + 1].cells[colInd].appendChild(createPiece(col));
      }
    });
  });

  // sets up each player's hand
  const topPieces = document.getElementById("top-pieces");
  const botPieces = document.getElementById("bottom-pieces");
  for (let i = 2; i <= 8; i++) {
    const dropPiece = document.createElement("div");
    dropPiece.style.backgroundImage = `url(${pieceArt[pieceMap[i]]})`;
    dropPiece.classList.add("drop-piece");
    dropPiece.classList.add(pieceMap[i]);
    dropPiece.setAttribute("counter", 0);
    const topDropPiece = dropPiece.cloneNode();
    dropPiece.classList.add(playerColorStr);
    topDropPiece.classList.add(playerColor === 1 ? "white" : "black");
    topDropPiece.style.transform = "scaleY(-1)";

    topPieces.rows[0].cells[8 - i].appendChild(topDropPiece);
    botPieces.rows[0].cells[8 - i].appendChild(dropPiece);
  }
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

// sets each td element to align center
document.querySelectorAll("td").forEach((cell) => {
  cell.setAttribute("align", "center");
});

// clears marked destination squares
const clearDestCells = () => {
  document.querySelectorAll(".move-dest").forEach((el) => {
    el.classList.remove("move-dest", "promote");
    el.removeAttribute("visited");
  });
};

htmlBoard.addEventListener("click", clearDestCells);
