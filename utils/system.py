def kill_port(port):
    """杀死占用端口的进程（Linux/Mac/Windows）"""
    try:
        if os.name == "nt":  # Windows
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", str(port)],
                capture_output=True,
                text=True,
                shell=True,
            )
            if result.stdout:
                pid = result.stdout.strip().split()[-1]
                subprocess.run(["taskkill", "/PID", pid, "/F"], shell=True)
        else:  # Linux/Mac
            subprocess.run(
                f"lsof -ti:{port} | xargs kill -9",
                shell=True,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass  # 忽略错误
