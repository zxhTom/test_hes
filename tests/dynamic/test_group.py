import pytest
import allure
import json
from pytest_check import check
import random
from jsonpath_rw import parse
from psycopg2 import sql


@allure.feature("limit group")
@allure.story("dynamic group limit by device's protocol")
@allure.title("Limit Device Protocol Group")
@allure.severity(allure.severity_level.CRITICAL)
# @pytest.mark.skip(reason="developping，avoid log record")
def test_get_dynamic_limit_protocol_group(project_root, api_client, pg_connect):
    cur = pg_connect.cursor()
    multiple_type_sql = """
    select 
    '01' as device_type,
    cm.meter_id as device_id,dmm.protocol_id 
    from c_meter cm
    left join d_meter_model dmm on dmm.model_id=cm.model_id
    where cm.is_delete='01'
    union all
    select 
    '02' as device_type,
    rtr.tmnl_id as device_id,dtm.protocol_id
    from r_tmnl_run rtr
    left join d_tmnl_model dtm on dtm.model_id=rtr.model_id
    where rtr.is_delete='01'
    """
    cur.execute(
        multiple_type_sql,
    )
    tables = cur.fetchall()
    meters = [row for row in tables if row[0] == "01"]
    tmnls = [row for row in tables if row[0] == "02"]
    url = "/api/quality/set"
    sub_meters = random.sample(meters, min(2, len(meters)))
    sub_meter_ids = [str(row[1]) for row in sub_meters]
    sub_meter_protocol_ids = [int(str(row[2])) for row in sub_meters if row[2] != None]
    sub_tmnl = random.sample(tmnls, min(2, len(tmnls)))
    sub_tmnl_ids = [str(row[1]) for row in sub_tmnl]
    sub_tmnl_protocol_ids = [int(str(row[2])) for row in sub_tmnl if row[2] != None]
    body = {"meterType": "01", "deviceIdList": sub_meter_ids}
    with allure.step("search meter's device dynamic groups folder"):
        allure.attach(
            body=json.dumps(body, indent=2, ensure_ascii=False),
            name="meters",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json=body)  # 10秒超时
    with allure.step("search meter's device dynamic groups response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name="meters",
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert response.json()["httpStatus"] == 200
    jsonpath_expr = parse("$..groupId")
    groups = [match.value for match in jsonpath_expr.find(response.json()["data"])]
    if len(groups) == 0:
        groups.append(-1)
    gplaceholders = ",".join(["%s"] * len(groups))
    pplaceholders = ",".join(["%s"] * len(sub_tmnl_protocol_ids))
    query = """
        SELECT 
        distinct pg.group_id 
        FROM p_group pg 
        left join p_obis_group pog 
        on pg.group_id=pog.group_id 
        WHERE pg.group_id = ANY(%s) 
        and pog.protocol_id = ANY(%s)
        """
    cur.execute(query, (groups, sub_meter_protocol_ids))
    tables = cur.fetchall()
    with check:
        assert len(tables) == len(groups)
    body = {"meterType": "02", "deviceIdList": sub_tmnl_ids}
    with allure.step("search tmnl's device dynamic groups folder"):
        allure.attach(
            body=json.dumps(body, indent=2, ensure_ascii=False),
            name="tmnl",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(url, json=body)  # 10秒超时
    with allure.step("search tmnl's device dynamic groups response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name="tmnl",
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert response.json()["httpStatus"] == 200
    jsonpath_expr = parse("$..groupId")
    groups = [match.value for match in jsonpath_expr.find(response.json()["data"])]
    if len(groups) == 0:
        groups.append(-1)
    gplaceholders = ",".join(["%s"] * len(groups))
    pplaceholders = ",".join(["%s"] * len(sub_tmnl_protocol_ids))
    query = """
        SELECT 
        distinct pg.group_id 
        FROM p_group pg 
        left join p_obis_group pog 
        on pg.group_id=pog.group_id 
        WHERE pg.group_id = ANY(%s) 
        and pog.protocol_id = ANY(%s)
        """
    cur.execute(query, (groups, sub_tmnl_protocol_ids))
    tables = cur.fetchall()
    groups.remove(-1)
    with check:
        assert len(tables) == len(groups)
