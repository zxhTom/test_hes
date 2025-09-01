import pytest
import allure
import json
from utils.check_utils import check
from utils.data import is_json_and_type as isjson

task_list = "/api/metering-task/get-metering-task"
detail_url = {
    "1": {
        "select": "/api/metering-task/getTaskSelectedTerminal",
        "unselect": "/api/metering-task/getTaskUnSelectedTerminal",
        "target": "/api/tmnl-run/page",
    },
    "8": {
        "select": "/api/metering-task/getTaskSelectedTag",
    },
    "3": {
        "select": "/api/metering-task/getTaskSelectedMeter",
        "unselect": "/api/metering-task/getTaskUnSelectedMeter",
        "target": "/api/meters/loadDeviceInfoAndOnlineStatus",
    },
}
template = {"pageNum": 1, "pageSize": 100, "conditions": []}


@allure.feature("get and valid task")
@allure.story("get task list , and valid obj count")
@allure.title("metering task")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_metering_valid(api_client):
    with allure.step("task list"):
        allure.attach(
            body=json.dumps(template, indent=2, ensure_ascii=False),
            name="task list payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(task_list, json=template)
    with allure.step("task list response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name="task list response",
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert response.json()["httpStatus"] == 200
    filter_rows = [
        row
        for row in response.json().get("data")["list"]
        if row["collObjType"] in detail_url
    ]
    for row in filter_rows:
        old_count = row["objDetailCount"]
        task_id = row["taskId"]
        collobjtype = row["collObjType"]
        count_url = detail_url.get(collobjtype)["select"]
        sub_json = {
            "taskId": task_id,
            "pageNum": 1,
            "collObjType": collobjtype,
            "pageSize": 100,
            "orgNo": "100",
        }
        with allure.step("selected list payload"):
            allure.attach(
                body=json.dumps(sub_json, indent=2, ensure_ascii=False),
                name="selected payload," + count_url,
                attachment_type=allure.attachment_type.JSON,
            )
        response = api_client.post(count_url, json=sub_json)
        with allure.step("selected list response"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name="selected list",
                attachment_type=allure.attachment_type.JSON,
            )
        with check:
            assert response.json()["httpStatus"] == 200
        total = response.json().get("data").get("total")
        with check:
            assert old_count == total
        if "unselect" in detail_url.get(collobjtype):
            un_count_url = detail_url.get(collobjtype)["unselect"]
            sub_json = {
                "taskId": task_id,
                "pageNum": 1,
                "collObjType": collobjtype,
                "pageSize": 100,
                "orgNo": "100",
            }
            with allure.step("unselected list payload"):
                allure.attach(
                    body=json.dumps(sub_json, indent=2, ensure_ascii=False),
                    name="unselected payload," + un_count_url,
                    attachment_type=allure.attachment_type.JSON,
                )
            response = api_client.post(un_count_url, json=sub_json)
            with allure.step("unselected list response"):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name="unselected list",
                    attachment_type=allure.attachment_type.JSON,
                )
            with check:
                assert response.json()["httpStatus"] == 200
            unselectedtotal = response.json().get("data").get("total")
            target_body = {
                "pageNum": 1,
                "pageSize": 100,
                "conditions": [],
                "orgNo": "100",
                "lineIds": [],
                "tranIds": [],
                "substationIds": [],
            }
            target_url = detail_url.get(collobjtype)["target"]
            with allure.step("target list payload"):
                allure.attach(
                    body=json.dumps(target_body, indent=2, ensure_ascii=False),
                    name="target payload," + target_url,
                    attachment_type=allure.attachment_type.JSON,
                )
            response = api_client.post(target_url, json=target_body)
            with allure.step("target list response"):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name="target list" + target_url,
                    attachment_type=allure.attachment_type.JSON,
                )
            targettotal = response.json().get("data").get("total")
            assert targettotal == total + unselectedtotal
