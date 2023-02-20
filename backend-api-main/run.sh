
gunicorn -b 0.0.0.0:8080 --timeout=20 --worker-class=uvicorn.workers.UvicornWorker --workers=2 main:app
