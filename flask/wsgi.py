import os

#from waitress import serve
from main import create_app
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

try:
    with open("server.pid", "w") as f:
        f.write(str(os.getpid()))
except Exception as e:
    print(f"Error writing PID: {e}")

application = create_app()

#  if __name__ == "__main__":
#    serve(application, host='0.0.0.0', port=5000)
