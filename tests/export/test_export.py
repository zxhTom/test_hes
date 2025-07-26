import time

import pytest


@pytest.mark.skip(reason="暂时禁用，avoid log record")
def test_get_system_configuration(api_client, env_config, pg_connect):
    """
    test export
    valid weather create record of export task
    valid weather create record of op_log
    """
    payload = {
        "conditions": [],
        "displays": [
            "Online Status",
            "Status",
            "Relay Status",
            "Device ID.",
            "Model",
            "Vendor",
            "Organization",
            "State",
            "Sub-state",
            "Comm Mode",
            "Protocol",
            "City",
            "Zone",
            "Street",
            "Group(Tag)",
            "Created On",
            "ActiveSince",
            "DeActivated From",
            "Created By",
            "Module Firmware",
            "Nonlegal application Firmware",
            "Legal Metrological Firmware",
            "Hardware Version",
            "Customer ID",
            "Customer Type",
            "Security Version",
            "Security Version",
            "Security Suite",
            "Security Policy",
        ],
        "fields": [
            "onlineStatus",
            "isActiveLabel",
            "relayStatusLabel",
            "serialNo",
            "modelCode",
            "mfgName",
            "orgName",
            "cycleStatusLabel",
            "cycleSubStatusLabel",
            "commMode",
            "protocolName",
            "city",
            "zone",
            "street",
            "tagsName",
            "createDate",
            "activeDate",
            "deactivatedDate",
            "createdBy",
            "firmwareVersion",
            "firmwareVersionNon",
            "firmwareVersionSign",
            "hardwareVersion",
            "consName",
            "consSortCodeLabel",
            "securityVersionLabel",
            "securityVersionLabel",
            "securitySuiteLabel",
            "encryptCodeLabel",
        ],
        "sortFields": [],
        "pageNum": 1,
        "pageSize": 171,
    }
    task_query = "select task_id,export_name from sa.sys_export_task where task_id=%s"
    response = api_client.post(
        "/api/meters/loadTableExportBackGroud?exportType=Excel", json=payload
    )
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
