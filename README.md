# Shogi-Learning

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
