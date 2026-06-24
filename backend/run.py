"""
Startup script that waits for MySQL to become available
before launching the FastAPI application.
Essential for Docker Compose where containers start concurrently.
"""

import os
import socket
import time
import uvicorn


def wait_for_mysql(host: str, port: int, timeout: int = 60):
    """Block until a TCP connection to MySQL succeeds or timeout is reached."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, port))
            s.close()
            print(f"MySQL is ready at {host}:{port}")
            return
        except (socket.error, socket.timeout):
            print(f"Waiting for MySQL at {host}:{port}...")
            time.sleep(2)
    raise ConnectionError(f"MySQL not available at {host}:{port} after {timeout}s")


if __name__ == "__main__":
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = int(os.getenv("MYSQL_PORT", "3306"))

    wait_for_mysql(mysql_host, mysql_port)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEV_MODE", "false").lower() == "true"
    )