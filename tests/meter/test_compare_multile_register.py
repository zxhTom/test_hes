import random
import pytest

from pytest_check import check
from utils.date import generate_random_time_range as timerange


def test_compare_device(api_client, env_config, pg_connect):
    cur = pg_connect.cursor()
    multiple_meter_sql = "select cm.meter_id from c_meter cm where cm.is_delete ='01' order by random() limit 10 	;"
    cur.execute(multiple_meter_sql)
    tables = cur.fetchall()
    meter_id_list = [int(row[0]) for row in tables]
    single_group_sql = "select pg.group_id from p_group pg where pg.group_type ='2' order by random() limit 1"
    cur.execute(single_group_sql)
    group_id = int(cur.fetchone()[0])
    start, end = timerange(min_duration_hours=72, max_duration_hours=168)
    payload = {
        "deviceIds": meter_id_list,
        "startTime": start.strftime("%Y-%m-%d %H:%M:%S"),
        "endTime": end.strftime("%Y-%m-%d %H:%M:%S"),
        "groupId": group_id,
    }
    print(payload)
    response = api_client.post(
        "/api/kpi/device/deviceRegisterLatestValue", json=payload
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
            if None == datav and fetchdata == None:
                with check:
                    assert True
            elif datav != None and fetchdata != None:
                with check:
                    assert datav == fetchdata[0]
            else:
                with check:
                    assert False
    elif kpi_data["messageCode"] == "31002":
        assert True
    else:
        assert False
