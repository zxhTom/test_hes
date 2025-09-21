import pytest


# 全局 token fixture
@pytest.fixture(scope="session")
def language():
    language = {"language": "en", "country": "us"}
    return language
