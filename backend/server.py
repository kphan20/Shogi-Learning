from flask import Flask
from flask_socketio import SocketIO, send

# add secret key later
app = Flask(__name__)
app.config["DEBUG"] = True
socketio = SocketIO(app)


@socketio.on("json")
def handle_message(data):
    print(data)
    send(data)


if __name__ == "__main__":
    socketio.run(app)
