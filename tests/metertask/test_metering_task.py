import pytest
import allure
import json
from utils.check_utils import check
from utils.data import is_json_and_type as isjson
import pandas as pd


def deduplicate_by_attr(objects, attr, keep="first"):
    """
    按照指定属性去重，可选择保留第一个或最后一个

    Args:
        objects: 对象列表
        attr: 要去重的属性名
        keep: 保留策略，'first'或'last'

    Returns:
        去重后的对象列表
    """
    if keep == "last":
        objects = objects[::-1]

    seen = set()
    result = []
    for obj in objects:
        attr_value = obj.get(attr)
        if attr_value not in seen:
            seen.add(attr_value)
            result.append(obj)

    if keep == "last":
        return result[::-1]
    return result


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
            name=f"task list response,{task_list}",
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert response.json()["httpStatus"] == 200
    filter_rows = [
        row
        for row in response.json().get("data")["list"]
        if row["collObjType"] in detail_url
    ]
    # result = list({obj.collObjType: obj for obj in filter_rows}.values())
    result = deduplicate_by_attr(filter_rows, "collObjType")
    # result=filter_rows
    for row in result:
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
                name="selected list"+count_url,
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
                    name="unselected list"+un_count_url,
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
