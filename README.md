# Shogi-Learning

## Overview

I started this project after becoming fascinated with reinforcement learning and shogi at around the same time. I wanted to learn more about how training models to learn complex games would work, so I hoped to be able to do that by applying different models to the game of shogi. I have accomplished the following so far-

- I built a graphical interface with Electron.js to learn about the framework and potentially release a desktop app.
- I also built a Flask backend that uses sockets to communicate with the Electron app, facilitating the transfer of moves from models running in the backend to the frontend. You can currently play against a random AI.
- Based heavily on [this project](https://github.com/suragnair/alpha-zero-general/), I have established a training infrastructure to approximate/recreate the Alpha-Zero algorithm. Still working on training this model.

I hope to eventually extend the project to the point where

- I have multiple trained models to play against.
- I can pit these models against each other.
- I currently have the frontend setup to only handle player vs AI matches, but designing it to handle PvP and visualize AI v AI sounds interesting.

## Running the project

This project was developed on a Windows device, so command may vary depending on the OS.

Clone the repository:

```
git clone https://github.com/kphan20/Shogi-Learning.git
```

There are two sets of instructions from here on in - one for the backend and one for the frontend/GUI.

### Backend

After navigating to the backend folder, it is recommended to initialize a virtual environment. Here, I use venv:

```
python -m venv [venv_name]
venv_name/scripts/activate
```

Install the dependencies in the requirements.txt file. Be warned that I included a version of torch in the file. Currently, I am thinking of hosting all of the backend functionality on my local computer (including pytorch), but there are probably alternative ways of doing it (perhaps through Google Colab?).

```
pip install -r requirements.txt
```

### Frontend

Within the frontend folder, to install the dependencies (mainly Electron), you can use npm:

```
npm install
```
