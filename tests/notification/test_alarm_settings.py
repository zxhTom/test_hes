import pytest
import allure
import json
from jsonpath_rw import parse
from utils.check_utils import check
import jmespath

unit_tests = [
    (
        "/api/meters/notificationTypeSettings",
        "type",
        "select type ,is_enabled from sys_notification_type_config where user_id=%s",
        "data[*].{source:source,isNotice:isNotice}",
    ),
    (
        "/api/meters/notificationChannelSettings",
        "channel",
        "select channel,is_enabled from sys_notification_channel_config where user_id=%s",
        "data[*].{source:source,isNotice:isNotice}",
    ),
    (
        "/api/meters/meterAlarmNoticeList",
        "meter",
        "select object_id ,'true' from sys_notification_object_subscription where user_id=%s",
        "data[*].configurationList[*].{source:id,isNotice:isNotice} | []",
    ),
    (
        "/api/meters/terminalAlarmNoticeList",
        "terminal",
        "select object_id,'true' from sys_notification_object_subscription where user_id=%s",
        "data[*].configurationList[*].{source:id,isNotice:isNotice} | []",
    ),
]


@allure.feature("alarm settings")
@allure.story("settings save and select")
@allure.title("notifications")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("url,module,sql,format_parse", unit_tests)
def test_check_status(url, module, sql, format_parse, api_client, pg_connect):
    cur = pg_connect.cursor()
    user_sql = "select user_id from sa.sys_user su where su.user_name = 'zxhtomapi'"
    cur.execute(
        user_sql,
        (),
    )
    user_id = str(cur.fetchone()[0])
    cur.execute(sql, (user_id,))
    items = [row for row in cur.fetchall()]
    result = dict(items)
    response = api_client.post(url, json={})
    with check:
        assert response.json()["httpStatus"] == 200
    with allure.step(f"{module} data list"):
        allure.attach(
            body=json.dumps(response.json(), indent=2, ensure_ascii=False),
            name=f"{module} respnse",
            attachment_type=allure.attachment_type.JSON,
        )
    if response.json()["data"] != None:
        # 修改后的JSONPath表达式，添加别名
        api_res = jmespath.search(format_parse, response.json())
        for char_item in api_res:
            assert char_item["isNotice"] == (str(char_item["source"]) in result)
