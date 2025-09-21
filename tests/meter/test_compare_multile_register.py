import random
import pytest
import allure
import json
from pytest_check import check
from utils.date import generate_random_time_range as timerange


@allure.feature("registers function")
@allure.story("base devices get registers")
@allure.title("valid device register compare")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_register_from_meter(api_client, env_config, pg_connect):
    type_url = "/api/profile/meter/profileType"
    profile_list_response = api_client.post(type_url, json={})
    with check:
        assert profile_list_response.json()["httpStatus"] == 200
    with allure.step("profile request payload"):
        allure.attach(
            body=json.dumps(profile_list_response.json(), indent=2, ensure_ascii=False),
            name="request response",
            attachment_type=allure.attachment_type.JSON,
        )
    profiles = profile_list_response.json()["data"]
    profileids = [row.get("groupId") for row in profiles]
    url = "/api/profile/meter/DateItem"
    cur = pg_connect.cursor()
    multiple_meter_sql = "select cm.meter_id from c_meter cm where cm.is_delete ='01' order by random() limit 10 	;"
    cur.execute(multiple_meter_sql)
    tables = cur.fetchall()
    meter_id_list = [int(row[0]) for row in tables]
    for profileid in profileids:
        meterid = random.choice(meter_id_list)
        body = {"meterId": meterid, "profileId": profileid}
        response = api_client.post(type_url, json={})
        with check:
            assert response.json()["httpStatus"] == 200
        with allure.step("meter dataitem list"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name="dataitem response",
                attachment_type=allure.attachment_type.JSON,
            )
        body = {"meterIds": meter_id_list, "profileId": profileid}
        response = api_client.post(type_url, json={})
        with check:
            assert response.json()["httpStatus"] == 200
        with allure.step("meters dataitem list"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name="dataitem response",
                attachment_type=allure.attachment_type.JSON,
            )


@allure.feature("compare function")
@allure.story("device register compare successful")
@allure.title("valid device register compare")
@allure.severity(allure.severity_level.CRITICAL)
def test_compare_device(api_client, env_config, pg_connect):
    cur = pg_connect.cursor()
    multiple_meter_sql = "select cm.meter_id from c_meter cm where cm.is_delete ='01' order by random() limit 10 	;"
    cur.execute(multiple_meter_sql)
    tables = cur.fetchall()
    meter_id_list = [int(row[0]) for row in tables]
    with allure.step("get random meter list 10"):
        allure.attach(str(meter_id_list), "MeterIdList")
    single_group_sql = "select pg.group_id from p_group pg where pg.group_type ='2' order by random() limit 1"
    cur.execute(single_group_sql)
    group_id = int(cur.fetchone()[0])
    with allure.step("get random register"):
        allure.attach(str(group_id), "Group")
    start, end = timerange(min_duration_hours=72, max_duration_hours=168)
    payload = {
        "deviceIds": meter_id_list,
        "startTime": start.strftime("%Y-%m-%d %H:%M:%S"),
        "endTime": end.strftime("%Y-%m-%d %H:%M:%S"),
        "groupId": group_id,
    }
    print(payload)
    with allure.step("record real payload"):
        allure.attach(
            body=json.dumps(payload, indent=2, ensure_ascii=False),
            name="request payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(
        "/api/kpi/device/deviceRegisterLatestValue", json=payload
    )
    with allure.step("record real response..."):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name="/api/kpi/device/deviceRegisterLatestValue",
            attachment_type=allure.attachment_type.JSON,
        )
    kpi_data = response.json()
    # print(kpi_data)
    if kpi_data["httpStatus"] == 200:
        datelist = kpi_data["data"]["horizontalOrdinates"]
        vertialslist = kpi_data["data"]["vertials"]
        if vertialslist != None and len(vertialslist) > 0:
            print("loaded data.........................................")
            random_num = random.randrange(0, len(vertialslist))
            datas = vertialslist[random_num]["datas"]
            random_num = random.randrange(0, len(datas))
            datav = datas[random_num]
            datev = datelist[random_num]
            meter_id = random.choice(meter_id_list)
            group_info_sql = "select db_table,db_field from p_group where group_id=%s and db_table is not null and db_field is not null"
            cur.execute(group_info_sql, (group_id,))
            group = cur.fetchone()
            tableName = group[0]
            fieldName = group[1]
            get_data_sql = f"""
            select {fieldName} from {tableName} ddr 
            left join r_mp rm on rm.mp_id =ddr.mp_id 
            left join c_meter cm on cm.meter_id =rm.meter_id 
            where cm.meter_id=%s
            and ddr.data_date=%s
            """
            cur.execute(
                get_data_sql,
                (
                    meter_id,
                    datev,
                ),
            )
            fetchdata = cur.fetchone()
            if(datav!=0 and datav!='0'):
                if (None == datav or datav==0) and fetchdata == None:
                    with check:
                        assert True
                elif datav != None and fetchdata != None:
                    with check:
                        assert datav == fetchdata[0]
                else:
                    with allure.step("compare data is different"):
                        allure.attach(
                            body=f"datav={datav},fetchdata={fetchdata}",
                            name="compare left and right",
                            attachment_type=allure.attachment_type.TEXT,
                        )
                    with check:
                        assert False
    elif kpi_data["messageCode"] == "31002":
        assert True
    else:
        assert False
