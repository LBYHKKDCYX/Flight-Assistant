import os
import sys

try:
    from app import app
except ModuleNotFoundError as e:
    print(f"缺少库: {e}")
    raise SystemExit(1)

if __name__ == '__main__':
    if os.name == 'nt':  # Windows
        try:
            from waitress import serve
            serve(app, host='0.0.0.0', port=5000, threads=4)
        except ModuleNotFoundError as e:
            print(f"缺少库: {e}")
            raise SystemExit(1)
    else:  # Linux / macOS
        try:
            from gunicorn.app.wsgiapp import run
            sys.argv = ['gunicorn', 'wsgi:app', '-b', '0.0.0.0:5000', '-w', '4']
            run()
        except ModuleNotFoundError as e:
            print(f"缺少库: {e}")
            raise SystemExit(1)
