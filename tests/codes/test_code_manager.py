from utils.check_utils import check
import allure
import json
import string
import random
# 生成指定长度的随机字符串（包含字母和数字）
def random_string(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@allure.feature("create codes store 2 appropriate db field")
@allure.story("I want create some dict codes in multiple languages")
@allure.title("Code Operators")
@allure.severity(allure.severity_level.CRITICAL)
def test_code_insert(api_client, env_config, pg_connect):
    code_table_sql="select table_id from sys_code_table where name='DEBUG_CODES'"
    code_item_sql="select count(1)+1 from sys_code_item where table_id=%s"
    cursor=pg_connect.cursor()
    cursor.execute(code_table_sql)
    table_info=cursor.fetchone()
    table_id=int(table_info[0])
    dynamic_content_field=["code","label","description"]
    insert_url="/api/code/operitem"
    code_insert_param={
        "id": None,
        "label2": None,
        "code": "nihao",
        "label": "w",
        "description": "w",
        "orderNum": 1,
        "isEditable": "0",
        "tableId": 3785,
        "flag": "1"
    }
    cursor.execute(code_item_sql,(table_id,))
    items=cursor.fetchone()
    order_num=items[0]
    code_insert_param["orderNum"]=order_num
    code_insert_param["tableId"]=table_id
    template=random_string()
    for dcf in dynamic_content_field:
        last_content=f"{dcf}_{template}"
        code_insert_param[dcf]=last_content
    print(code_insert_param)
    with allure.step("insert code params"):
        allure.attach(
            body=json.dumps(code_insert_param, indent=2, ensure_ascii=False),
            name=insert_url,
            attachment_type=allure.attachment_type.JSON,
        )
    response=api_client.post(insert_url,json=code_insert_param)
    with allure.step("insert code response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=insert_url,
            attachment_type=allure.attachment_type.JSON,
        )
    with check: assert response.json()["httpStatus"]==200


@allure.feature("modify codes store 2 appropriate db field")
@allure.story("I want update some dict codes in multiple languages")
@allure.title("Code Operators")
@allure.severity(allure.severity_level.CRITICAL)
def test_code_update(api_client, env_config, pg_connect):
    code_item_sql="select id,table_id,order_num from sys_code_item where table_id=(select table_id from sys_code_table where name='DEBUG_CODES')"
    cursor=pg_connect.cursor()
    cursor.execute(code_item_sql)
    item_info=cursor.fetchone()
    table_id=int(item_info[1])
    order_num=int(item_info[2])
    id=int(item_info[0])
    dynamic_content_field=["code","label","description"]
    insert_url="/api/code/operitem"
    code_update_param={
        "id": 3789,
        "label2": None,
        "code": "code_Ipip3wqd3",
        "label": "5",
        "description": "4r",
        "orderNum": 1,
        "isEditable": "0",
        "tableId": 3785,
        "flag": "2"
    }
    code_update_param["orderNum"]=order_num
    code_update_param["tableId"]=table_id
    code_update_param["id"]=id
    template=random_string()
    for dcf in dynamic_content_field:
        last_content=f"{dcf}_{template}"
        code_update_param[dcf]=last_content
    print(code_update_param)
    with allure.step("update code params"):
        allure.attach(
            body=json.dumps(code_update_param, indent=2, ensure_ascii=False),
            name=insert_url,
            attachment_type=allure.attachment_type.JSON,
        )
    response=api_client.post(insert_url,json=code_update_param)
    with allure.step("update code response"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=insert_url,
            attachment_type=allure.attachment_type.JSON,
        )
    with check: assert response.json()["httpStatus"]==200
