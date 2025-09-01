from pytest_check import check
import allure
import json


@allure.feature("generate and compare function")
@allure.story("generate random conditon and value , test right")
@allure.title("Condition Generator")
@allure.severity(allure.severity_level.CRITICAL)
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
            with allure.step("get conditions in menu and group by loop"):
                allure.attach(
                    body=json.dumps(payload, indent=2, ensure_ascii=False),
                    name="within group conditions,menu:" + str(menuId),
                    attachment_type=allure.attachment_type.JSON,
                )
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
        with allure.step("get conditions only in menu"):
            allure.attach(
                body=json.dumps(payload, indent=2, ensure_ascii=False),
                name="single menu conditon,menu:" + str(menuId),
                attachment_type=allure.attachment_type.JSON,
            )
        response = api_client.post(
            "/api/dynamic/condition/selectConditionableFieldEntire", json=payload
        )
        with allure.step("get conditions only in menu response"):
            allure.attach(
                body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                name="entire" + str(menuId),
                attachment_type=allure.attachment_type.JSON,
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
                    with allure.step("get conditions errors, menu" + str(menuId)):
                        allure.attach(
                            body=json.dumps(payload, indent=2, ensure_ascii=False),
                            name="error conditon,menu:" + str(menuId),
                            attachment_type=allure.attachment_type.JSON,
                        )
