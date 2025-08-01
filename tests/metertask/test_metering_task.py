import pytest
import allure
import json
from pytest_check import check
from utils.data import is_json_and_type as isjson

task_list = "/api/metering-task/get-metering-task"
detail_url = {
    "1": "/api/metering-task/getTaskSelectedTerminal",
    "8": "/api/metering-task/getTaskSelectedTag",
    "3": "/api/metering-task/getTaskSelectedMeter",
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
        count_url = detail_url.get(collobjtype)
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
