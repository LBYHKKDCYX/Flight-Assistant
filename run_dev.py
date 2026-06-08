import subprocess
import sys
import os
import time
import webbrowser
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_DIR = os.path.join(BASE_DIR, 'backend')
VUE_DIR = os.path.join(BASE_DIR, 'frontend')

flask_proc = None
vue_proc = None

def print_banner():
    print("""
╔══════════════════════════════════════╗
║              ✈️一键启动               ║
║                                      ║
║  Flask:  http://localhost:5000       ║
║  Vue:    http://localhost:5173       ║
╚══════════════════════════════════════╝
    """)

def check_dependencies():
    print("[检测依赖]")
    try:
        from flask_cors import CORS
        print("  ✅ flask-cors 已安装")
    except ImportError:
        print("  ⏳ flask-cors 未安装，正在自动安装...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'flask-cors'],
            cwd=FLASK_DIR, capture_output=True
        )
        print("  ✅ flask-cors 安装完成")

    npm_path = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'nodejs', 'npm.cmd')
    alt_npm = os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'nodejs', 'npm.cmd')
    if not os.path.exists(npm_path) and not os.path.exists(alt_npm):
        npm_path = 'npm.cmd'

    node_modules = os.path.join(VUE_DIR, 'node_modules')
    if not os.path.exists(node_modules):
        print("  ⏳ Vue 依赖未安装，正在自动安装...")
        subprocess.run(
            ['cmd', '/c', 'npm', 'install'],
            cwd=VUE_DIR, shell=True
        )
        print("  ✅ Vue 依赖安装完成")
    else:
        print("  ✅ Vue 依赖已安装")
    print()

def start_flask():
    global flask_proc
    print("[1/2] 正在启动 Flask 后端...")
    flask_proc = subprocess.Popen(
        [sys.executable, 'run.py'],
        cwd=FLASK_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )

    for line in flask_proc.stdout:
        print(f"  [Flask] {line}", end='')
        if 'Running on' in line:
            break

    print("  ✅ Flask 后端启动成功\n")

def start_vue():
    global vue_proc
    print("[2/2] 正在启动 Vue 前端...")
    vue_proc = subprocess.Popen(
        ['cmd', '/c', 'npx', 'vite', '--host'],
        cwd=VUE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )

    for line in vue_proc.stdout:
        print(f"  [Vue] {line}", end='')
        if 'Local:' in line:
            break

    print("  ✅ Vue 前端启动成功\n")
    print("  浏览器已自动打开")

def cleanup():
    print("\n正在关闭服务...")
    if vue_proc:
        vue_proc.terminate()
        try:
            vue_proc.wait(timeout=5)
        except:
            vue_proc.kill()
        print("  ✅ Vue 已关闭")
    if flask_proc:
        flask_proc.terminate()
        try:
            flask_proc.wait(timeout=5)
        except:
            flask_proc.kill()
        print("  ✅ Flask 已关闭")
    print("  再见! ✈️")

if __name__ == '__main__':
    print_banner()
    check_dependencies()
    start_flask()
    start_vue()

    webbrowser.open('http://localhost:5173')

    print("按 Ctrl+C 停止所有服务")

    def signal_handler(sig, frame):
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
