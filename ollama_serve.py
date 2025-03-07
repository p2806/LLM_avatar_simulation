import subprocess
import os
import time

def start_ollama_server():
    """
    Start the Ollama server programmatically if not already running.
    """
    try:
        # Check if the Ollama server is already running
        response = subprocess.run(["curl", "http://localhost:11434/"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if response.returncode == 0:
            print("Ollama server is already running.")
            return

        # Start the Ollama server
        print("Starting Ollama server...")
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,  # Prevent termination when the script ends
        )
        time.sleep(2)  # Give it a moment to start

        # Check if the server started successfully
        response = subprocess.run(["curl", "http://localhost:11434/"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if response.returncode == 0:
            print("Ollama server started successfully.")
        else:
            print("Failed to start Ollama server. Check the logs for details.")

    except Exception as e:
        print(f"An error occurred while starting the Ollama server: {e}")



def kill_ollama():
    """
    Stop the Ollama server by killing its process.
    """
    try:
        # Attempt to kill the Ollama server process
        subprocess.run(["pkill", "-f", "ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Ollama server stopped successfully.")
    except Exception as e:
        print(f"An error occurred while stopping the Ollama server: {e}")

if __name__ == "__main__":
    kill_ollama()