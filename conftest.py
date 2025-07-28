import pytest
import requests
import os
from pathlib import Path
import redis
import json

pytest_plugins = [
    "fixtures.database",  # 自动发现 fixtures/database.py 中的 Fixture
]
# 环境配置管理
@pytest.fixture(scope="session")
def env_config():
    """根据环境变量加载对应的配置"""
    env = os.getenv("TEST_ENV", "dev")
    config_path = Path(__file__).parent / "config/private" / f"{env}.json"

    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        pytest.fail(f"环境配置文件 {config_path} 不存在")


# Token 管理器
class TokenManager:
    def __init__(self, env_config):
        self.env_config = env_config
        self._token = None
        self._token_file = Path(".token")

    def get_token(self):
        """获取 token，如果不存在或已过期则重新获取"""
        if not self._token and self._token_file.exists():
            self._token = self._token_file.read_text().strip()

        if not self._token or self._is_token_expired():
            self._token = self._fetch_new_token()
            self._token_file.write_text(self._token)

        return self._token

    def _fetch_new_token(self):
        """调用登录接口获取新 token"""
        pool = redis.ConnectionPool(
            port=self.env_config["redis"]["port"],
            host=self.env_config["redis"]["host"],
            db=self.env_config["redis"]["database"],
            password=self.env_config["redis"]["password"],  # 如果有密码
            decode_responses=True,  # 自动解码为字符串
        )
        r = redis.Redis(connection_pool=pool)
        mkeys = r.keys("user-token:zxhtomapi:*")
        if len(mkeys) > 0:
            return r.get(mkeys[0])
        else:
            return ""

    def _is_token_expired(self):
        """检查 token 是否过期（简化实现）"""
        # 实际项目中可能需要解析 JWT 或调用验证接口
        return False


# 全局 token fixture
@pytest.fixture(scope="session")
def token_manager(env_config):
    """创建全局 TokenManager 实例"""
    return TokenManager(env_config)


# API 客户端 fixture
@pytest.fixture
def api_client(env_config, token_manager):
    """返回配置好的 API 客户端"""

    class APIClient:
        def __init__(self, base_url, token_manager):
            self.base_url = base_url
            self.token_manager = token_manager

        def get(self, path, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self.token_manager.get_token()}"
            return requests.get(f"{self.base_url}{path}", headers=headers, **kwargs)

        def post(self, path, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self.token_manager.get_token()}"
            return requests.post(f"{self.base_url}{path}", headers=headers, **kwargs)

    return APIClient(env_config["base_url"], token_manager)
