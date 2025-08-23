import pytest
import allure
import json
from jsonpath_rw import parse
from utils.check_utils import check
import jmespath


@allure.feature("alarm settings")
@allure.story("settings save and select")
@allure.title("notifications")
@allure.severity(allure.severity_level.CRITICAL)
def test_alarm_event_list_page(api_client, pg_connect):
    url = "/api/meters/alarmEnventDeviceListPage"
    param = {"orgNo": "100"}
    response = api_client.post(url, json=param)
    with check:
        assert response.json()["httpStatus"] == 200
