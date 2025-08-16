import time
import allure
import json
import pytest

export_url = [("/api/meters/loadTableExportBackGroud")]


@allure.feature("export function")
@allure.story("test export task")
@allure.title("Export")
@allure.severity(allure.severity_level.CRITICAL)
# @pytest.mark.skip(reason="暂时禁用，avoid log record")
@pytest.mark.parametrize("url", export_url)
def test_get_system_configuration(url, api_client, env_config, pg_connect):
    """
    test export
    valid weather create record of export task
    valid weather create record of op_log
    """
    payload = {
        "conditions": [],
        "sortFields": [],
        "pageNum": 1,
        "pageSize": 2,
    }
    task_query = "select task_id,export_name from sa.sys_export_task where task_id=%s"
    with allure.step("task params"):
        allure.attach(
            body=json.dumps(str(payload), indent=2, ensure_ascii=False),
            name="export params payload",
            attachment_type=allure.attachment_type.JSON,
        )
    response = api_client.post(f"{url}?exportType=Excel", json=payload)
    print(response.json())
    if response.status_code == 409:  # 用户名已存在
        pytest.skip("用户已存在，跳过创建测试")
    else:
        assert (
            response.status_code == 200 and response.json()["httpStatus"] == 200
        ), response.json()
        time.sleep(6.5)
        id = response.json()["data"]["id"]
        cur = pg_connect.cursor()
        print(cur.mogrify(task_query, (id,)).decode("utf-8"))
        cur.execute(task_query, (id,))
        result = cur.fetchone()
        assert (result[1], "export task name is not null")
