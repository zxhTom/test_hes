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
            "fieldKey": "comm_mode",
            "fieldType": "String",
            "operator": "in",
            "values": ["1"],
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
def test_get_cycle(
    generate_test_pairs, type, targeturl, api_client, env_config, pg_connect
):

    response = api_client.post("/api/kpi/visualization/commType", json={})
    commtypes = [row["code"] for row in response.json()["data"]]
    for commtype in commtypes:
        for before in generate_test_pairs:
            before["commType"] = commtype
            print(before)
            meter_param.update(before)
            print(meter_param)
            with allure.step("group payload"):
                allure.attach(
                    body=json.dumps(before, indent=2, ensure_ascii=False),
                    name="/api/kpi/device/onlineCycleStatusStatics",
                    attachment_type=allure.attachment_type.JSON,
                )
            response = api_client.post(
                "/api/kpi/device/onlineCycleStatusStatics", json=before
            )
            with allure.step("group response"):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name="/api/kpi/device/onlineCycleStatusStatics",
                    attachment_type=allure.attachment_type.JSON,
                )
            bt = response.json().get("data")["total"]
            typecondition = {
                "fieldKey": "comm_mode",
                "fieldType": "String",
                "operator": "in",
                "values": ["1"],
            }
            values = [commtype]
            typecondition["values"] = values
            meter_param["conditions"] = [typecondition]
            with allure.step("meter param payload"):
                allure.attach(
                    body=json.dumps(meter_param, indent=2, ensure_ascii=False),
                    name=targeturl,
                    attachment_type=allure.attachment_type.JSON,
                )
            response = api_client.post(
                "/api/meters/loadDeviceInfoAndOnlineStatus", json=meter_param
            )
            typecondition = {
                "fieldKey": "wan_comm_mode",
                "fieldType": "String",
                "operator": "in",
                "values": ["1"],
            }
            values = [commtype]
            typecondition["values"] = values
            meter_param["conditions"] = [typecondition]
            rresponse = api_client.post("/api/tmnl-run/page", json=meter_param)
            with allure.step("meter response"):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name=targeturl,
                    attachment_type=allure.attachment_type.JSON,
                )
            with allure.step("tmnl response"):
                allure.attach(
                    body=json.dumps(rresponse.json(), indent=2, ensure_ascii=False),
                    name=targeturl,
                    attachment_type=allure.attachment_type.JSON,
                )
            meterOnlineTotal = response.json()["data"].get("total")
            tmnlOnlineTotal = rresponse.json()["data"].get("total")
            with check:
                assert bt == meterOnlineTotal + tmnlOnlineTotal
