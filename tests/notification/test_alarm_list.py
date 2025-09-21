import pytest
import allure
import json
from jsonpath_rw import parse
from utils.check_utils import check
import jmespath
import random

eventalarmgroups = [
    ("/api/meters/alarmEnventDeviceListPage", "/api/meters/alarmEnventDeviceDetails"),
    (
        "/api/tmnl-run/alarmEnventDeviceListPage",
        "/api/tmnl-run/alarmEnventDeviceDetails",
    ),
]


@allure.feature("alarm settings")
@allure.story("settings save and select")
@allure.title("notifications")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("url,details_url", eventalarmgroups)
def test_alarm_event_list_page(url, details_url, api_client, pg_connect):
    param = {"orgNo": "100", "pageSize": 2000}
    with allure.step(f"list page parameter"):
        allure.attach(
            body=json.dumps(param, indent=2, ensure_ascii=False),
            name=f"{url}",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json=param)
    with allure.step(f"list page response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=f"{url}",
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert response.json()["httpStatus"] == 200
    res_json = response.json()
    datas = res_json["data"]["list"]
    cur = pg_connect.cursor()
    eventalarm_sql = (
        "select field_name from sys_raw_date_configuration srdc where raw_type ='50'"
    )
    cur.execute(
        eventalarm_sql,
        (),
    )
    tables = cur.fetchall()
    single_tables = [row[0] for row in tables]
    for row in single_tables:
        item_data = [item[row] for item in datas if item[row] is not None]
        if len(item_data) <= 0:
            with allure.step(f"list page response"):
                allure.attach(
                    body=row,
                    name=f"{url}",
                    attachment_type=allure.attachment_type.TEXT,
                )
            assert False

    # 分别获取 event 和 alarm 类型的数据
    event_data = [item for item in datas if item["type"] == "Event"]
    alarm_data = [item for item in datas if item["type"] == "Alarm"]

    # 随机抽取各3条数据
    random_events = random.sample(event_data, min(2, len(event_data)))
    random_alarms = random.sample(alarm_data, min(2, len(alarm_data)))
    sample_datas = random_events + random_alarms
    details_body = {
        "groupId": "",
        "deviceId": "",
        "eventCode": "",
        "subEventCode": "",
        "mpId": "",
        "itemId": "",
        "itemType": "",
    }
    for sd in sample_datas:
        details_body["groupId"] = sd["groupId"]
        details_body["deviceId"] = sd["deviceId"]
        details_body["eventCode"] = sd["eventCode"]
        details_body["subEventCode"] = sd["subEventCode"]
        details_body["mpId"] = sd["mpId"]
        details_body["itemId"] = sd["id"]
        details_body["itemType"] = sd["type"]
        with allure.step(f"details page parameter"):
            allure.attach(
                body=json.dumps(details_body, indent=2, ensure_ascii=False),
                name=f"{details_url}",
                attachment_type=allure.attachment_type.JSON,
            )
        detailsresponse = api_client.post(details_url, json=details_body)
        details_json = detailsresponse.json()
        with allure.step(f"details page response"):
            allure.attach(
                body=json.dumps(details_json, indent=2, ensure_ascii=False),
                name=f"{details_url}",
                attachment_type=allure.attachment_type.JSON,
            )
        with check:
            assert details_json["httpStatus"] == 200
        detailstotal = details_json["data"]["total"]
        assert detailstotal == sd["occurrenceCount"]
