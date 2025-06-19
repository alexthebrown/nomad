from flask import Flask, request, jsonify, render_template_string
import threading
import socket # Import socket for graceful shutdown

class WebServer:
    def __init__(self, control_state):
        self.control_state = control_state
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        
        @self.app.route("/", methods=["GET"])
        def index():
            # You'll need to make sure the 'templates/index.html' file exists
            try:
                with open("./templates/index.html") as f:
                    html = f.read()
                return render_template_string(html)
            except FileNotFoundError:
                return "Index HTML file not found.", 404
            
        @self.app.route("/api/reset", methods=["POST"])
        def reset():
            self.control_state["reset"] = True
            self.control_state["logs"].append("Reset Command Received.")
            return "", 204

        @self.app.route("/api/shutdown", methods=["POST"])
        def shutdown():
            self.control_state["shutdown"] = True
            self.control_state["logs"].append("Shutdown command received.")
            try:
                # Send a dummy request to the server to unblock it
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", 5002))  # Replace 5002 with your actual port
                s.sendall(b'GET / HTTP/1.0\r\n\r\n')
                s.close()
            except Exception as e:
                print(f"Error sending dummy request to shutdown server: {e}")

            return "", 204

        @self.app.route("/api/logs", methods=["GET"])
        def logs():
            return jsonify(self.control_state["logs"][-100:])

    def run(self):
        """Runs the Flask development server."""
        # The stop_event is managed in the main thread,
        # so it's not directly used in the run method here

        try:
            self.app.run(host="0.0.0.0", port=5002)  # Replace 5002 with your actual port
        except Exception as e:
            print(f"Error in web server thread: {e}")
            # The stop_event should be handled by the calling function (nomad_web_server_thread)
            # if the server crashes unexpectedly.
