import pytest


# 全局 token fixture
@pytest.fixture(scope="session")
def language():
    language = {"language": "es", "country": "es"}
    return language
