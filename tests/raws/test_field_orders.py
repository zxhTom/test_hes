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


@allure.feature("orders function")
@allure.story("generate random orders and value , search")
@allure.title("Orders Generator And Search")
@allure.severity(allure.severity_level.CRITICAL)
def test_generate_orders_check_search_not_error(
    project_root, api_client, pg_connect, request
):
    with open(
        os.path.join(project_root, "config", "raw.json"), "r", encoding="utf-8"
    ) as f:
        cur = pg_connect.cursor()
        raw_info_sql = (
            "select * from sys_raw_date_configuration srdc where srdc.raw_type=%s"
        )
        data = json.load(f)  # 自动解析为Python列表
        # 遍历数组
        for item in data:
            if isinstance(item, dict):
                rawType = item.get("rawType")
                cur.execute(raw_info_sql, (rawType,))
                tables = cur.fetchall()
                fieldNames = [row[3] for row in tables]
                sorts = []
                for fn in fieldNames:
                    single_sort = {}
                    single_sort["filed"] = fn
                    single_sort["sort"] = "descend"
                    sorts.append(single_sort)
                print(sorts)
                urls = item.get("url")
                params = {}
                params["sortFields"] = sorts
                for url in urls:
                    with allure.step("check no orders"):
                        allure.attach(
                            body=json.dumps(params, indent=2, ensure_ascii=False),
                            name=f"{url}",
                            attachment_type=allure.attachment_type.JSON,
                        )
                    response = api_client.post(url, json={})
                    with allure.step("check no orders responses"):
                        allure.attach(
                            body=json.dumps(
                                response.json(), indent=2, ensure_ascii=False
                            ),
                            name=f"{url}",
                            attachment_type=allure.attachment_type.JSON,
                        )
                    assert response.json()["httpStatus"] == 200
                    with allure.step("check orders"):
                        allure.attach(
                            body=json.dumps(params, indent=2, ensure_ascii=False),
                            name=f"{url}",
                            attachment_type=allure.attachment_type.JSON,
                        )
                    response = api_client.post(url, json=params)
                    with allure.step("check orders responses"):
                        allure.attach(
                            body=json.dumps(
                                response.json(), indent=2, ensure_ascii=False
                            ),
                            name=f"{url}",
                            attachment_type=allure.attachment_type.JSON,
                        )
                    assert response.json()["httpStatus"] == 200
