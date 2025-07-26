from pytest_check import check


def test_get_condition_list(api_client, env_config, pg_connect):
    support_menus_sql = "select distinct menu_id from sys_query_field"
    cur = pg_connect.cursor()
    cur.execute(support_menus_sql)
    tables = cur.fetchall()
    for table in tables:
        menuId = table[0]
        if menuId == 1132 or menuId == 24993:
            continue
        multiple_org_sql = "select org_no from sa.sys_org so where so.org_no like %s order by org_no limit 2"
        cur.execute(multiple_org_sql, ("100%",))
        orgs = cur.fetchall()
        for org in orgs:
            payload = {
                "menuId": str(menuId),
                "parentCode": str(org[0]),
                "fieldLabel": "Group ID",
            }
            response = api_client.post(
                "/api/dynamic/condition/selectConditionableFieldEntire", json=payload
            )
            data = response.json()["data"]
            for item in data:
                if (
                    "ConTree" == item["componentProps"]
                    or "ConSelect" == item["componentProps"]
                ):

                    with check:
                        assert item["componentSelectList"][0]["code"] == str(org[0])
                    if item["componentSelectList"][0]["code"] != str(org[0]):
                        print("---------------------------")
                        print(menuId)
                        print(payload)

        payload = {
            "menuId": str(menuId),
        }
        response = api_client.post(
            "/api/dynamic/condition/selectConditionableFieldEntire", json=payload
        )
        data = response.json()["data"]
        for item in data:
            if (
                "ConTree" == item["componentProps"]
                or "ConSelect" == item["componentProps"]
            ):
                with check:
                    assert len(item["componentSelectList"]) > 0
                if len(item["componentSelectList"]) == 0:
                    print("---------------------------")
                    print(menuId)
                    print(item)
