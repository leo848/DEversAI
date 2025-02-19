import os

app_path = os.environ["HOME"] + "/jufo2025/shallow-backend"

wsgi_app = "main:app"
bind = ":8000"
chdir = app_path
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
errorlog = app_path + "/errors.log"
