if __name__ == '__main__':
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ModuleNotFoundError as e:
        print(f"缺少库: {e}")
        raise SystemExit(1)
