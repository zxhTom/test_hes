import pytest
import allure
import json
from pytest_check import check

urls = [
    ("/api/substation/list"),
    ("/api/grid-management/tran/query"),
    ("/api/grid-management/line/query"),
    ("/api/tmnl-run/page"),
]


@allure.feature("common page's function")
@allure.story("page's params under valid")
@allure.title("valid page paramter")
@allure.severity(allure.severity_level.CRITICAL)
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
    with allure.step("get random register"):
        allure.attach(
            body=json.dumps(payload, indent=2, ensure_ascii=False),
            name="requst payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json=payload)
    assert response.json()["httpStatus"] == 200
    if response.json()["data"]["total"] > 2:
        payload["pageSize"] = 1
        subresponse = api_client.post(url, json=payload)
        assert response.json()["data"]["total"] == subresponse.json()["data"]["total"]
