import os
import pytest
from pytest_check import check
import allure
import json
import traceback
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
import requests
import stringcase
from jsonpath_rw import parse


def fetch_query_fields(menuId, pg_connect):
    """从PostgreSQL获取查询字段"""
    with pg_connect.cursor() as cursor:
        query = sql.SQL(
            """
            SELECT field_type, field_name,options,component_props,condition_id, multipleable ,ambiguous
            FROM sys_query_field where menu_id=%s
        """
        )
        cursor.execute(query, (menuId,))
        return cursor.fetchall()


def generate_value(
    field_type, field_name, options, component_props, multipeable, list, cons
):
    """根据字段类型生成示例值"""
    if field_type == "String":
        origin_field_name = field_name
        field_name = stringcase.camelcase(field_name)
        samples = [1, 2, 4, 5]
        try:
            if options != "":
                cursor = pg_connect.cursor()
                multiple_type_sql = "select code from sys_code_item sci where sci.table_id = (select table_id from sys_code_table sct where sct.name=%s)"
                cur.execute(multiple_type_sql, (options,))
                tables = cur.fetchall()
                samples = [item[0] for item in table]
            elif component_props != "ConSelect" and component_props != "ConTree":
                samples = [item[field_name] for item in list]
                samples = [x for x in samples if x is not None]
                if len(samples) == 0:
                    samples = [1, 2, 4, 5]
            else:
                filter_condition = next(
                    (row for row in cons if origin_field_name == row["conditionId"]),
                    None,
                )
                if (
                    filter_condition["componentSelectList"] != None
                    and len(filter_condition["componentSelectList"]) > 0
                ):

                    jsonpath_expr = parse("$..code")
                    samples = [
                        match.value for match in jsonpath_expr.find(filter_condition)
                    ]
        except Exception as e:
            samples = [1, 2, 4, 5]
        if multipeable:
            return random.sample(samples, min(2, len(samples)))
        return random.choice(samples)
    elif field_type == "Number":
        if multipeable:
            return [random.randint(1, 100), random.randint(1, 100)]
        return random.randint(1, 100)
    elif field_type == "Boolean":
        if multipeable:
            return ["true", "false"]
        return "true"
    elif field_type == "Date":
        date1 = datetime.now() - timedelta(days=random.randint(1, 30))
        date2 = date1 + timedelta(days=random.randint(1, 5))
        return [
            date1.strftime("%Y-%m-%d %H:%M:%S"),
            date2.strftime("%Y-%m-%d %H:%M:%S"),
        ]
    else:
        return "default_value"


def generate_operator(field_type, multipeable, ambiguous):
    """生成操作符"""
    if field_type == "Date":
        return "between"
    if multipeable:
        return "in"
    if ambiguous:
        return "like"
    return "="


def generate_json_output(menuId,list, conditions, fields):
    """生成最终JSON输出"""
    result = []
    for field in fields:
        (
            field_type,
            field_name,
            options,
            component_props,
            condition_id,
            multipeable,
            ambiguous,
        ) = field
        is_multi = multipeable == 1  # 假设multipeable是整数类型
        is_ambiguous = ambiguous == 1  # 假设multipeable是整数类型

        if component_props == "ConSelect" or component_props == "ConTree":

            samples = [
                selectList
                for item in conditions
                if item["fieldName"] == field_name
                for selectList in item["componentSelectList"]
            ]
            if len(samples) <= 0:
                with allure.step("check condition"):
                    allure.attach(
                        body=json.dumps(conditions, indent=2, ensure_ascii=False),
                        name=f"{menuId}@@@{field_name}",
                        attachment_type=allure.attachment_type.JSON,
                    )
                assert False

        result.append(
            {
                "fieldKey": condition_id,
                "fieldType": field_type,
                "operator": generate_operator(field_type, is_multi, is_ambiguous),
                "values": generate_value(
                    field_type,
                    field_name,
                    options,
                    component_props,
                    is_multi,
                    list,
                    conditions,
                ),
            }
        )
    return result


def get_all_keys(json_obj, parent_key=""):
    keys = set()
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            keys.add(full_key)
            keys.update(get_all_keys(v, full_key))
    elif isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            keys.update(get_all_keys(item, parent_key))
    return keys


template_param = {
    "pageNum": 1,
    "pageSize": 100,
    "orgNo": "100",
    "lineIds": [],
    "tranIds": [],
    "substationIds": [],
}


@allure.feature("generate and search function")
@allure.story("generate random conditon and value , search")
@allure.title("Condition Generator And Search")
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_noneandmulptile_condition(
    project_root, api_client, pg_connect, request
):
    # 读取JSON文件
    with open(
        os.path.join(project_root, "config", "request.json"), "r", encoding="utf-8"
    ) as f:
        data = json.load(f)  # 自动解析为Python列表
        # 遍历数组
        for item in data:
            if isinstance(item, dict):
                menuId = item.get("menuId")
                if menuId in [114997]:
                    continue
                    print("slow....>>>>")
                    request.node.add_marker(pytest.mark.slow)
                url = item.get("url")
                print(f"ID: {item.get('menuId')}, Name: {url}")

                fields = fetch_query_fields(menuId, pg_connect)
                conditions = []
                with allure.step("generate none paramter condition page"):
                    allure.attach(
                        body=json.dumps(template_param, indent=2, ensure_ascii=False),
                        name=url,
                        attachment_type=allure.attachment_type.JSON,
                    )
                template_param["conditions"] = conditions
                response = api_client.post(url, json=template_param)  # 10秒超时
                with allure.step("none condition,response"):
                    allure.attach(
                        body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                        name=str(url),
                        attachment_type=allure.attachment_type.JSON,
                    )
                assert response.json()["httpStatus"]==200
                condition_res = api_client.post(
                    "/api/dynamic/condition/selectConditionableFieldEntire",
                    json={"menuId": menuId},
                )
                cons = condition_res.json()["data"]
                # print(response.json())
                list = response.json()["data"]["list"]
                # 生成条件列表
                conditions = generate_json_output(menuId,list, cons, fields)
                template_param["conditions"] = conditions

                a_values = [
                    item["fieldKey"] for item in conditions if "fieldKey" in item
                ]

                with allure.step(
                    "will generate some condition,len=" + str(len(a_values))
                ):
                    allure.attach(
                        body=json.dumps(template_param, indent=2, ensure_ascii=False),
                        name=str(url),
                        attachment_type=allure.attachment_type.JSON,
                    )
                response = api_client.post(url, json=template_param)  # 10秒超时
                with allure.step("condition,response=" + str(len(a_values))):
                    allure.attach(
                        body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                        name=str(url),
                        attachment_type=allure.attachment_type.JSON,
                    )
                if response.json()["httpStatus"] == 200:
                    assert True
                else:
                    print(response.json())
                    assert False
