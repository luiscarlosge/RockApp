"""
Gunicorn configuration for Azure App Service Linux deployment
Optimized for Flask-SocketIO applications with WebSocket support
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"  # Required for SocketIO
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1200
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'rock-app-linux'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (handled by Azure)
keyfile = None
certfile = None

# Environment variables for the application
raw_env = [
    f'FLASK_ENV={os.environ.get("FLASK_ENV", "production")}',
    f'FLASK_DEBUG={os.environ.get("FLASK_DEBUG", "False")}',
    f'PYTHONPATH={os.environ.get("PYTHONPATH", "/home/site/wwwroot")}',
    f'WEBSITE_HOSTNAME={os.environ.get("WEBSITE_HOSTNAME", "")}',
    f'PORT={os.environ.get("PORT", "8000")}',
    'WEBSOCKET_ENABLED=true',
    'SOCKETIO_ASYNC_MODE=eventlet',
    'SOCKETIO_PING_TIMEOUT=60',
    'SOCKETIO_PING_INTERVAL=25'
]

# Preload application for better performance
def on_starting(server):
    server.log.info("Starting Gunicorn server for Rock App Linux")

def on_reload(server):
    server.log.info("Reloading Gunicorn server")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    worker.log.info(f"Worker initialized (pid: {worker.pid})")

def worker_abort(worker):
    worker.log.info(f"Worker received SIGABRT signal (pid: {worker.pid})")