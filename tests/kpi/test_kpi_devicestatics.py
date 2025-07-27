import pytest
import allure
import json
from pytest_check import check


@pytest.fixture
def generate_test_pairs(pg_connect):
    res = []
    cur = pg_connect.cursor()
    multiple_org_sql = "select org_no from sa.sys_org so where so.org_no like %s order by org_no limit 2"
    cur.execute(multiple_org_sql, ("100%",))
    tables = cur.fetchall()
    for table in tables:
        item = {
            "orgNo": str(table[0]),
            "lineIds": [],
            "tranIds": [],
            "substationIds": [],
            "deviceType": "01",
        }
        res.append(item)
    return res


@allure.feature("compare function")
@allure.story("compare different group result")
@allure.title("Compare Group")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_deviceTypeStatics(generate_test_pairs, api_client, env_config, pg_connect):
    before = generate_test_pairs[0]
    after = generate_test_pairs[1]
    with allure.step("first group payload"):
        allure.attach(
            body=json.dumps(before, indent=2, ensure_ascii=False),
            name="requst payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post("/api/kpi/device/deviceTypeStatics", json=before)
    beforedata = response.json()["data"]
    with allure.step("after group payload"):
        allure.attach(
            body=json.dumps(after, indent=2, ensure_ascii=False),
            name="requst payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post("/api/kpi/device/deviceTypeStatics", json=after)
    afterdata = response.json()["data"]
    bt = beforedata["total"]
    at = afterdata["total"]
    if bt != 0 or at != 0:
        with check:
            assert bt != at


@pytest.fixture
def deviceTypeList(pg_connect):
    res = []
    cur = pg_connect.cursor()
    multiple_type_sql = "select code from sys_code_item sci where sci.table_id = (select table_id from sys_code_table sct where sct.name='ASSET_STATICS_DEVICE_TYPE')"
    cur.execute(
        multiple_type_sql,
    )
    tables = cur.fetchall()
    for table in tables:
        item = {
            "deviceType": str(table[0]),
        }
        res.append(item)
    return res


@allure.feature("multiple function")
@allure.story("multiple devicetype response")
@allure.title("Multiple DeviceType")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_multiple_type_valid(deviceTypeList, api_client, env_config, pg_connect):
    for typeBody in deviceTypeList:
        with allure.step("loop single deviceType"):
            allure.attach(
                body=json.dumps(typeBody, indent=2, ensure_ascii=False),
                name="deviceType payload",
                attachment_type=allure.attachment_type.JSON,
            )
        response = api_client.post("/api/kpi/device/deviceTypeStatics", json=typeBody)
        with check:
            assert response.json()["httpStatus"] == 200


topconditions = [
    (
        "03",
        "SUBSTATION.TYPE",
        "substationIds",
        "SELECT substation_id FROM g_substation where is_delete='01' ORDER BY RANDOM() LIMIT 2;",
        "/api/substation/list",
    ),
    (
        "05",
        "LINE_TYPE",
        "lineIds",
        "SELECT line_id FROM g_line where is_delete='01' ORDER BY RANDOM() LIMIT 2;",
        "/api/grid-management/line/query",
    ),
    (
        "04",
        "TRAN.TYPE",
        "tranIds",
        "SELECT tran_id FROM g_tran where is_delete='01' ORDER BY RANDOM() LIMIT 2;",
        "/api/grid-management/tran/query",
    ),
]


@allure.feature("compare function")
@allure.story("statics right and essential to page list")
@allure.title("Valid Statics Data")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("type,code,fieldName,exeSql,url", topconditions)
def test_get_top_condition(
    deviceTypeList, type, code, fieldName, exeSql, url, api_client, pg_connect
):
    cur = pg_connect.cursor()
    multiple_type_sql = "select label_zhcn,label_en from sys_code_item sci where sci.table_id = (select table_id from sys_code_table sct where sct.name=%s)"
    cur.execute(
        multiple_type_sql,
        (code,),
    )
    codes = cur.fetchall()
    codes_zh = [row[0] for row in codes]
    with allure.step("list zh language codes"):
        allure.attach(
            body=json.dumps(str(codes_zh), indent=2, ensure_ascii=False),
            name="code zh list",
            attachment_type=allure.attachment_type.TEXT,
        )
    codes_en = [row[1] for row in codes]
    with allure.step("list en language codes"):
        allure.attach(
            body=json.dumps(str(codes_en), indent=2, ensure_ascii=False),
            name="code en list",
            attachment_type=allure.attachment_type.TEXT,
        )
    cur.execute(
        exeSql,
    )
    tables = cur.fetchall()
    rows = [int(row[0]) for row in tables]
    item = {fieldName: rows, "deviceType": type, "pageNum": 1, "pageSize": 10}
    print(item)
    with allure.step("statics paramter"):
        allure.attach(
            body=json.dumps((item), indent=2, ensure_ascii=False),
            name="request payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post("/api/kpi/device/deviceTypeStatics", json=item)
    kpiTotal = response.json()["data"]["total"]
    names = [row["name"] for row in response.json()["data"]["statics"]]
    difference = [x for x in names if x not in codes_zh and x not in codes_en]
    with check:
        assert response.json()["httpStatus"] == 200
    with check:
        assert len(difference) == 0
    response = api_client.post(url, json=item)
    with check:
        assert response.json()["data"]["total"] == kpiTotal
