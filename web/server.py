from flask import Flask, request, jsonify, render_template_string
import threading

app = Flask(__name__)

control_state = {
    "shutdown": False,
    "reset": False,
    "logs": ["Nomad system initialized..."]
}
# Log storage (for display in web UI)
log_messages = ["Nomad system initialized..."]

@app.route("/", methods=["GET"])
def index():
    html = open("templates/index.html").read()
    return render_template_string(html)

@app.route("/api/reset", methods=["POST"])
def reset():
    control_state["reset"] = True
    control_state["logs"].append("Reset Command Recieved.")
    return "", 204

@app.route("/api/shutdown", methods=["POST"])
def shutdown():
    control_state["shutdown"] = True
    control_state["logs"].append("🔻 Shutdown command received.")
    return "", 204

@app.route("/api/logs", methods=["GET"])
def logs():
    return jsonify(control_state["logs"][-100:])

def log_event(msg):
    control_state["logs"].append(msg)
    print(msg)

def get_control_flags():
    return control_state

def run_server():
    thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5002))
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    run_server()
