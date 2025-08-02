import pytest
import allure
import json
from pytest_check import check

device_type = [
    ("01", "/api/meters/loadDeviceInfoAndOnlineStatus"),
    ("02", "/api/tmnl-run/page"),
]
meter_param = {
    "pageNum": 1,
    "pageSize": 2,
    "orgNo": "100",
    "conditions": [
        {
            "fieldKey": "online_status",
            "fieldType": "String",
            "operator": "in",
            "values": ["GREEN"],
        }
    ],
    "lineIds": [],
    "tranIds": [],
    "substationIds": [],
}


@allure.feature("compare function")
@allure.story("compare different group result")
@allure.title("Dynamic Group Online Statics")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("type,targeturl", device_type)
def test_get_onlineStatusStatics(
    generate_test_pairs, type, targeturl, api_client, env_config, pg_connect
):
    for before in generate_test_pairs:
        before["deviceType"] = type
        print(before)
        meter_param.update(before)
        print(meter_param)
        with allure.step("group payload"):
            allure.attach(
                body=json.dumps(before, indent=2, ensure_ascii=False),
                name="/api/kpi/device/onlineStatusStatics",
                attachment_type=allure.attachment_type.JSON,
            )
        response = api_client.post("/api/kpi/device/onlineStatusStatics", json=before)
        with allure.step("group response"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name="/api/kpi/device/onlineCycleStatusStatics",
                attachment_type=allure.attachment_type.JSON,
            )
        bt = response.json().get("data")["total"]
        with allure.step("target param payload"):
            allure.attach(
                body=json.dumps(meter_param, indent=2, ensure_ascii=False),
                name=targeturl,
                attachment_type=allure.attachment_type.JSON,
            )
        response = api_client.post(targeturl, json=meter_param)
        with allure.step("target response"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name=targeturl,
                attachment_type=allure.attachment_type.JSON,
            )
        meterOnlineTotal = response.json()["data"].get("total")
        with check:
            assert bt == meterOnlineTotal
