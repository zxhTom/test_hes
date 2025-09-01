import pytest
import allure
import json
from jsonpath_rw import parse
from utils.check_utils import check
import jmespath
import random

targets = [(1), (2)]


@allure.feature("alarm event linked")
@allure.story("linked obj manager")
@allure.title("linked obj manager")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("targetType", targets)
def test_linked_save(targetType, api_client, pg_connect):
    url = "/api/alarm_abstract/saveSubordinateLinkedObj"
    param = {
        "sourceId": 172,
        "sourceType": 2,
        "targetIdList": [286, 304],
        "targetType": targetType,
    }
    alarm_sql = "select * from p_obis_alarm_abstract poaa where is_active=true"
    cur = pg_connect.cursor()
    cur.execute(alarm_sql)
    tables = cur.fetchall()
    alarmIdList = [int(row[0]) for row in tables]
    sourceId = random.choice(alarmIdList)
    param["sourceId"] = sourceId
    target_obj_sql = """
        select alarm_id as id from p_obis_alarm_abstract poaa where is_active =true
        union all
        select event_id as id from sys_event_code_abstract seca
    """
    cur.execute(target_obj_sql)
    tables = cur.fetchall()
    targetIdList = [int(row[0]) for row in tables]
    targetIds = random.sample(targetIdList, random.randint(0, 5))
    param["targetIdList"] = targetIds

    with allure.step("save linked"):
        allure.attach(
            body=json.dumps(param, indent=2, ensure_ascii=False),
            name=url,
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json=param)
    if response.json()["httpStatus"] == 200:
        assert True
        check_data_remain_linked_sql = "select * from sys_abstract_event_alarm_link where source_type=2 and source_id=%s and target_type = %s"
        cur.execute(check_data_remain_linked_sql, (sourceId, targetType))
        target_datas = cur.fetchall()
        assert 0 == len(targetIds) or len(target_datas) == len(targetIds)
    elif (
        response.json()["httpStatus"] == 500
        and response.json()["messageCode"] == "31004"
    ):
        if len(targetIds) > 3:
            assert True
        else:
            remain_count_sql = "select count(1) from sys_abstract_event_alarm_link where source_type=2 and source_id=%s and target_type!=%s"
            cur.execute(remain_count_sql, (sourceId, targetType))
            tables = cur.fetchone()
            assert (len(targetIds) + int(tables[0])) > 3

    with allure.step("save linked response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=url,
            attachment_type=allure.attachment_type.JSON,
        )


alarm_event = [
    ("1", "/api/event_abstract/page", "eventId", "11"),
    ("2", "/api/alarm_abstract/page", "alarmId", "10"),
]


@allure.feature("alarm event list")
@allure.story("alarm list")
@allure.title("alarm list")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("itemtype,url,name,tagType", alarm_event)
def test_alarm_list_page(itemtype,url,name,tagType,api_client, pg_connect):

    with allure.step("list"):
        allure.attach(
            body=json.dumps({}, indent=2, ensure_ascii=False),
            name=url,
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json={})

    with allure.step("list response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=url,
            attachment_type=allure.attachment_type.JSON,
        )
    if response.json()["httpStatus"] == 200:
        assert True
        if len(response.json()["data"]["list"]) > 0:
            first = response.json()["data"]["list"][0]
            for key in first:
                if key.endswith("Label"):
                    if first[key[:-5]] != None and first[key] == None:
                        assert False
            alarmIds = [int(row[name]) for row in response.json()["data"]["list"]]
            tags_sql = """
                select st.tags_name from sa.sys_tag_rel str 
                left join sa.sys_tags st on st.tags_id =str.tag_id 
                where st.target_type =%s
                and str.object_id = any(%s)
            """
            cur = pg_connect.cursor()
            cur.execute(
                tags_sql,
                (
                    tagType,
                    alarmIds,
                ),
            )
            tables = cur.fetchall()
            tags_names = [row[0] for row in tables]
            if len(tags_names) > 0:
                if first["tagsName"] != None:
                    interfaceTagsNames = first["tagsName"].split(",")
                    assert interfaceTagsNames <= tags_names


alarm_event = [
    ("1", "select * from sys_event_code_abstract where is_active=true", "alarmId"),
    ("2", "select * from p_obis_alarm_abstract poaa where is_active=true", "eventId"),
]


@pytest.mark.parametrize("itemtype,select_sql,name", alarm_event)
def test_alarm_linked_list(itemtype, select_sql, name, api_client, pg_connect):
    url = "/api/alarm_abstract/subordinateLinkedObjList"
    param = {"sourceId": 172, "sourceType": 1}
    cur = pg_connect.cursor()
    cur.execute(select_sql)
    tables = cur.fetchall()
    alarmIdList = [int(row[0]) for row in tables]
    sourceId = random.choice(alarmIdList)
    param["sourceId"] = sourceId
    param["sourceType"] = itemtype
    with allure.step("test subordinates params"):
        allure.attach(
            body=json.dumps(param, indent=2, ensure_ascii=False),
            name=url,
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json=param)
    with allure.step("test subordinates response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=url,
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert response.json()["httpStatus"] == 200
    with check:
        len(response.json()["data"]) < 3


alarm_event = [
    ("1", "/api/alarm_abstract/page", "eventId"),
    ("2", "/api/event_abstract/page", "alarmId"),
]


@pytest.mark.parametrize("itemtype,url,name", alarm_event)
def test_alarm_or_event_unselect_list(itemtype, url, name, pg_connect, api_client):
    detectUrls = {
        1: "/api/event_abstract/page",
        2: "/api/alarm_abstract/page",
    }
    detectNames = {
        1: "eventId",
        2: "alarmId",
    }
    cur = pg_connect.cursor()
    linked_sql = "select source_id,source_type,target_id from sys_abstract_event_alarm_link where target_type=%s ORDER BY RANDOM() limit 5"
    cur.execute(linked_sql, (itemtype))
    params = {}
    params["unselect"] = True
    tables = cur.fetchall()
    for row in tables:
        params["sourceId"] = int(row[0])
        params["sourceType"] = int(row[1])
        url = detectUrls[int(itemtype)]
        with allure.step("test unselect filter param"):
            allure.attach(
                body=json.dumps(params, indent=2, ensure_ascii=False),
                name=url,
                attachment_type=allure.attachment_type.JSON,
            )
        response = api_client.post(url, json=params)

        with allure.step("test unselect filter response"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name=url,
                attachment_type=allure.attachment_type.JSON,
            )
        name=detectNames[int(itemtype)]
        itemIds = [int(row.get(name)) for row in response.json()["data"]["list"]]
        assert int(row[2]) not in itemIds
