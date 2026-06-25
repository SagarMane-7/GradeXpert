from microservice import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PYTHON_PORT', 5002))
    print(f"[Python Microservice] Starting PDF Parser on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
