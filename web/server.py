from flask import Flask, request, jsonify, render_template_string
import threading
import socket
import time
import os # To create the templates directory if it doesn't exist

class WebServer:
    def __init__(self, control_state):
        self.control_state = control_state
        self.app = Flask(__name__)
        self._setup_routes()
        self.host = "0.0.0.0"
        self.port = 5002 # Define the port here for consistency

    def _setup_routes(self):
        
        @self.app.route("/", methods=["GET"])
        def index():
            # You'll need to make sure the 'templates/index.html' file exists
            template_path = "./templates/index.html"
            try:
                with open(template_path, "r") as f:
                    html = f.read()
                return render_template_string(html)
            except FileNotFoundError:
                self.control_state["logs"].append(f"Error: {template_path} not found.")
                return f"Index HTML file not found at {template_path}.", 404
            
        @self.app.route("/api/reset", methods=["POST"])
        def reset():
            self.control_state["reset"] = True
            self.control_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] Reset Command Received.")
            print(f"[{time.strftime('%H:%M:%S')}] Reset Command Received.")
            return "", 204

        @self.app.route("/api/shutdown", methods=["POST"])
        def shutdown():
            self.control_state["shutdown"] = True
            self.control_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] Shutdown command received.")
            print(f"[{time.strftime('%H:%M:%S')}] Shutdown command received.")
            
            # This is crucial for unblocking the app.run() call,
            # allowing the Flask development server to exit.
            try:
                # Connect to the server itself and make a dummy request
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Use self.host and self.port for consistency
                s.connect((self.host if self.host != '0.0.0.0' else '127.0.0.1', self.port))
                s.sendall(b'GET /shutdown_signal HTTP/1.0\r\n\r\n')
                s.close()
            except ConnectionRefusedError:
                # This is expected if the server is already shutting down or stopped
                print(f"[{time.strftime('%H:%M:%S')}] Connection refused during dummy request, server likely already stopping.")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error sending dummy request for shutdown: {e}")

            return "", 204

        @self.app.route("/api/logs", methods=["GET"])
        def logs():
            return jsonify(self.control_state["logs"][-100:]) # Return last 100 logs

    def run(self):
        """Runs the Flask development server."""
        self.control_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] Web server starting on http://{self.host}:{self.port}")
        print(f"[{time.strftime('%H:%M:%S')}] Web server starting on http://{self.host}:{self.port}")
        try:
            # use_reloader=False is important when running in a separate thread
            # as the reloader creates new processes which can cause issues.
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            self.control_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] Error in web server thread: {e}")
            print(f"[{time.strftime('%H:%M:%S')}] Error in web server thread: {e}")
        finally:
            self.control_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] Web server thread terminated.")
            print(f"[{time.strftime('%H:%M:%S')}] Web server thread terminated.")


if __name__ == "__main__":
    # --- Setup the templates directory and index.html ---
    template_dir = "./templates"
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        print(f"Created directory: {template_dir}")

    index_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Control Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #1a202c;
            color: #e2e8f0;
        }
        .container {
            background-color: #2d3748;
            border-radius: 0.75rem; /* rounded-xl */
            padding: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem; /* rounded-lg */
            font-weight: 600; /* font-semibold */
            transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        .btn-red {
            background-color: #ef4444; /* red-500 */
            color: white;
        }
        .btn-red:hover {
            background-color: #dc2626; /* red-600 */
            transform: translateY(-1px);
        }
        .btn-blue {
            background-color: #3b82f6; /* blue-500 */
            color: white;
        }
        .btn-blue:hover {
            background-color: #2563eb; /* blue-600 */
            transform: translateY(-1px);
        }
        .btn:active {
            transform: translateY(0);
            box-shadow: none;
        }
        #log-output {
            background-color: #1a202c;
            border: 1px solid #4a5568;
            min-height: 150px;
            max-height: 300px;
            overflow-y: scroll;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen">
    <div class="container w-full max-w-lg mx-auto">
        <h1 class="text-3xl font-bold text-center mb-6">LED Control Panel</h1>

        <div class="space-y-4">
            <button id="resetButton" class="btn btn-blue w-full">
                Reset LED State
            </button>
            <button id="shutdownButton" class="btn btn-red w-full">
                Shutdown Web Server
            </button>
        </div>

        <div class="mt-8">
            <h2 class="text-xl font-semibold mb-3">Logs</h2>
            <div id="log-output" class="p-4 rounded-md text-sm">
                Loading logs...
            </div>
        </div>
    </div>

    <script>
        document.getElementById('resetButton').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                if (response.ok) {
                    console.log('Reset command sent.');
                    updateLogs(); // Refresh logs after sending command
                } else {
                    console.error('Failed to send reset command.');
                }
            } catch (error) {
                console.error('Error during reset:', error);
            }
        });

        document.getElementById('shutdownButton').addEventListener('click', async () => {
            if (confirm('Are you sure you want to shut down the web server?')) {
                try {
                    const response = await fetch('/api/shutdown', { method: 'POST' });
                    if (response.ok) {
                        console.log('Shutdown command sent.');
                        // Optionally disable buttons or show a message after shutdown
                        document.getElementById('resetButton').disabled = true;
                        document.getElementById('shutdownButton').disabled = true;
                        document.getElementById('log-output').textContent += '\\nServer shutdown initiated. Page may become unresponsive.';
                    } else {
                        console.error('Failed to send shutdown command.');
                    }
                } catch (error) {
                    console.error('Error during shutdown:', error);
                    document.getElementById('log-output').textContent += '\\nError initiating shutdown. Check server logs.';
                }
            }
        });

        async function updateLogs() {
            try {
                const response = await fetch('/api/logs');
                const logs = await response.json();
                const logOutput = document.getElementById('log-output');
                logOutput.textContent = logs.join('\\n');
                logOutput.scrollTop = logOutput.scrollHeight; // Auto-scroll to bottom
            } catch (error) {
                console.error('Error fetching logs:', error);
                document.getElementById('log-output').textContent = 'Failed to load logs.';
            }
        }

        // Fetch logs initially and then every few seconds
        updateLogs();
        setInterval(updateLogs, 3000); // Update logs every 3 seconds
    </script>
</body>
</html>
    """
    index_html_path = os.path.join(template_dir, "index.html")
    with open(index_html_path, "w") as f:
        f.write(index_html_content)
    print(f"Created file: {index_html_path}")

    # --- Initialize control state ---
    # This dictionary simulates shared state that your web server
    # and other components (like LED control) would interact with.
    control_state = {
        "reset": False,
        "shutdown": False,
        "logs": ["Application started."],
        # Add other state variables as needed for your application
    }

    # --- Create and run the web server ---
    web_server = WebServer(control_state)

    # Run the Flask app in a separate thread
    # use_reloader=False is crucial here to prevent Flask from spawning
    # a second process, which can interfere with threading and shutdown.
    web_server_thread = threading.Thread(target=web_server.run)
    web_server_thread.daemon = True # Allow main program to exit even if thread is running
    web_server_thread.start()

    print(f"[{time.strftime('%H:%M:%S')}] Main thread monitoring control_state['shutdown']...")
    print(f"Access the web server at http://127.0.0.1:{web_server.port}")
    print("Press Ctrl+C in this terminal to stop the main program, or use the web UI to shut down.")

    # --- Main loop for monitoring shutdown or other control logic ---
    try:
        while not control_state["shutdown"]:
            # Simulate other main application logic here if needed
            # For development, we just wait and check the flag
            time.sleep(0.5) # Check every half second

            # Example of how you might handle 'reset' flag
            if control_state["reset"]:
                control_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] Main thread detected reset command. Resetting application state...")
                print(f"[{time.strftime('%H:%M:%S')}] Main thread detected reset command. Resetting application state...")
                # Add your actual reset logic here (e.g., reinitialize LED state, clear data)
                control_state["reset"] = False # Clear the flag

    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] KeyboardInterrupt detected. Signalling shutdown.")
        control_state["shutdown"] = True # Signal shutdown if Ctrl+C is pressed in main thread

    finally:
        # Ensure the web server thread is gracefully stopped
        if control_state["shutdown"]:
            print(f"[{time.strftime('%H:%M:%S')}] Waiting for web server thread to finish...")
            web_server_thread.join(timeout=5) # Give it some time to shut down
            if web_server_thread.is_alive():
                print(f"[{time.strftime('%H:%M:%S')}] Web server thread did not terminate gracefully. It might be stuck.")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Web server thread joined successfully.")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Main loop exited without shutdown signal.")
        
        print(f"[{time.strftime('%H:%M:%S')}] Main application terminated.")
