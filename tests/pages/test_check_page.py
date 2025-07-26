import pytest

from pytest_check import check

urls = [
    ("/api/substation/list"),
    ("/api/grid-management/tran/query"),
    ("/api/grid-management/line/query"),
    ("/api/tmnl-run/page"),
]


@pytest.mark.parametrize("url", urls)
def test_get_page_valid(url, api_client):
    payload = {
        "pageSize": 100,
        "pageNum": 1,
        "conditions": [],
        "orgNo": "100",
        "lineIds": [],
        "tranIds": [],
        "substationIds": [],
    }
    response = api_client.post(url, json=payload)
    assert response.json()["httpStatus"] == 200
    if response.json()["data"]["total"] > 2:
        payload["pageSize"] = 1
        subresponse = api_client.post(url, json=payload)
        assert response.json()["data"]["total"] == subresponse.json()["data"]["total"]
