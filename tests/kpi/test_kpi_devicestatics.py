import pytest
import allure
import json
from pytest_check import check


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
            name="/api/kpi/device/deviceTypeStatics",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post("/api/kpi/device/deviceTypeStatics", json=before)
    beforedata = response.json()["data"]
    with allure.step("after group payload"):
        allure.attach(
            body=json.dumps(after, indent=2, ensure_ascii=False),
            name="/api/kpi/device/deviceTypeStatics",
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
                name="/api/kpi/device/deviceTypeStatics",
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
        "SELECT substation_id FROM g_substation where is_delete='01' and is_active='true' ORDER BY RANDOM() LIMIT 2;",
        "/api/substation/list",
    ),
    (
        "05",
        "LINE_TYPE",
        "lineIds",
        "SELECT line_id FROM g_line where is_delete='01' and is_active='true' ORDER BY RANDOM() LIMIT 2;",
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
    deviceTypeList, type, code, fieldName, exeSql, url, api_client, pg_connect,language
):
    cur = pg_connect.cursor()
    multiple_type_sql = f"select label_{language['language']}_{language['country']} from sys_code_item sci where sci.table_id = (select table_id from sys_code_table sct where sct.name=%s)"
    cur.execute(
        multiple_type_sql,
        (code,),
    )
    codes = cur.fetchall()
    codes_dy = [row[0] for row in codes]
    with allure.step(f"list {language['language']} language codes"):
        allure.attach(
            body=json.dumps(str(codes_dy), indent=2, ensure_ascii=False),
            name=f"code {language['language']} list",
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
            name="/api/kpi/device/deviceTypeStatics",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post("/api/kpi/device/deviceTypeStatics", json=item)
    kpiTotal = response.json()["data"]["total"]
    names = [row["name"] for row in response.json()["data"]["statics"]]
    difference = [x for x in names if x not in codes_dy]
    with check:
        assert response.json()["httpStatus"] == 200
    with check:
        assert len(difference) == 0
    conditions = []
    condition={
      "fieldKey": "is_active",
      "fieldType": "String",
      "operator": "in",
      "values": [
        True
      ]
    }
    conditions.append(condition)
    item["conditions"]=conditions
    response = api_client.post(url, json=item)
    with check:
        assert response.json()["data"]["total"] == kpiTotal


device_types = [
    ("01", "/api/meters/loadDeviceInfoAndOnlineStatus"),
    ("02", "/api/tmnl-run/page"),
    (
        "03",
        "/api/substation/list",
    ),
    (
        "05",
        "/api/grid-management/line/query",
    ),
    (
        "04",
        "/api/grid-management/tran/query",
    ),
]
meter_param = {
    "pageNum": 1,
    "pageSize": 2,
    "orgNo": "100",
    "conditions": [
        {
            "fieldKey": "is_active",
            "fieldType": "Boolean",
            "operator": "in",
            "values": ["true"],
        }
    ],
    "lineIds": [],
    "tranIds": [],
    "substationIds": [],
}


@allure.feature("coordinate function")
@allure.story("compare horizontal total")
@allure.title("Compare total")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("deviceType,url", device_types)
def test_coordinate_total(deviceType, url, api_client, env_config, pg_connect):
    statics_body = {
        "orgNo": "100",
        "lineIds": [],
        "tranIds": [],
        "substationIds": [],
        "deviceType": "02",
    }
    statics_body["deviceType"] = deviceType
    statics_body.update(
        {k: meter_param[k] for k in statics_body.keys() & meter_param.keys()}
    )
    statics_url = "/api/kpi/device/deviceTypeStatics"
    with allure.step("statics payload"):
        allure.attach(
            body=json.dumps(statics_body, indent=2, ensure_ascii=False),
            name="deviceTypeStatics,url="+statics_url,
            attachment_type=allure.attachment_type.JSON,
        )
    statics_response = api_client.post(statics_url, json=statics_body)
    with allure.step("statics response"):
        allure.attach(
            body=json.dumps(statics_response.json(), indent=2, ensure_ascii=False),
            name="deviceTypeStatics,url="+statics_url,
            attachment_type=allure.attachment_type.JSON,
        )

    with check:
        assert statics_response.json()["httpStatus"] == 200
    device_response = api_client.post(url, json=meter_param)
    with check:
        assert device_response.json()["httpStatus"] == 200
    assert (
        device_response.json()["data"]["total"]
        == statics_response.json()["data"]["total"]
    )
