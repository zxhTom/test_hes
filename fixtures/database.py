import psycopg2
from psycopg2 import sql
import pytest


# 全局 token fixture
@pytest.fixture(scope="session")
def pg_connect(env_config):
    print(env_config)
    # 连接参数
    conn_params = {
        "host": env_config["db"]["host"],
        "port": env_config["db"]["port"],
        "user": env_config["db"]["user"],  # 如果有密码
        "password": env_config["db"]["password"],  # 自动解码为字符串
        "database": env_config["db"]["database"],
        "keepalives": 1,  # 启用 keepalive
        "keepalives_idle": 30,  # 空闲30秒后开始发送keepalive包
        "keepalives_interval": 10,  # 每隔10秒发送一次keepalive
        "keepalives_count": 3,  # 最多发送3次未响应后断开
    }
    # 建立连接
    try:
        return psycopg2.connect(**conn_params)
    except psycopg2.Error as e:
        print(f"连接失败: {e}")
