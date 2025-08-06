import pytest
import allure
import json
from pytest_check import check
import random
from jsonpath_rw import parse
from psycopg2 import sql

devices = [
    (
        "01",
        "/api/meters/loadDeviceInfoAndOnlineStatus",
        {
            "pageNum": 1,
            "pageSize": 100,
            "showBalanceMeter": False,
            "conditions": [],
            "orgNo": "100",
            "lineIds": [],
            "tranIds": [],
            "substationIds": [],
        },
    ),
    (
        "02",
        "/api/tmnl-run/page",
        {
            "pageNum": 1,
            "pageSize": 100,
            "orderByFields": [],
            "conditions": [],
            "orgNo": "100",
            "lineIds": [],
            "tranIds": [],
            "substationIds": [],
        },
    ),
]


@allure.feature("map details")
@allure.story("base device dis , get device details")
@allure.title("device map details")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("deviceType,url,body", devices)
def test_get_map_device_details(deviceType, url, body, api_client, pg_connect):
    main_url = "/api/kpi/device/deviceDetails?serialNo=%s&deviceType=%s"
    response = api_client.post(url, json=body)
    assert response.json()["httpStatus"] == 200
    deviceNos = [row["serialNo"] for row in response.json()["data"]["list"]]
    for deviceNo in deviceNos:
        detailUrl = main_url % (deviceNo, deviceType)
        with allure.step("combine device info"):
            allure.attach(
                body=json.dumps(detailUrl, indent=2, ensure_ascii=False),
                name="default",
                attachment_type=allure.attachment_type.TEXT,
            )
        detailsResponse = api_client.post(detailUrl, json={})
        assert detailsResponse.json()["httpStatus"] == 200
