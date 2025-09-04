import pytest
import allure
import json
from jsonpath_rw import parse
from utils.check_utils import check
import jmespath
import random
import string
from psycopg2 import sql


@allure.feature("alarm event subscribe list")
@allure.story("device subscribe settings manager")
@allure.title("device subscribe settings manager")
@allure.severity(allure.severity_level.CRITICAL)
def test_linked_save(api_client, pg_connect):
    subscribe_url = "/api/meters/meterAlarmNoticeList"
    response = api_client.post(subscribe_url, json={})
    assert response.json()["httpStatus"] == 200
    datas = response.json()["data"]
    cur = pg_connect.cursor()
    for data in datas:
        if len(data["configurationList"]) > 0:
            alarmIds = [item["id"] for item in data["configurationList"]]
            print(alarmIds)
            alarm_active_sql = "select * from p_obis_alarm_abstract where alarm_id=any(%s) and is_active=true"
            cur.execute(alarm_active_sql, (alarmIds,))
            tables = cur.fetchall()
            assert len(tables) == len(alarmIds)
