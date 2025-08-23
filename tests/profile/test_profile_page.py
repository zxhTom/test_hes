import pytest
import allure
import json

# from pytest_check import check
from utils.check_utils import check
from jsonpath_rw import parse
import random
from utils.date import generate_random_time_range as timerange

template = {
    "pageNum": 1,
    "pageSize": 500,
    "sortFields": [],
    "orgNo": "100",
    "grpId": None,
    "grpType": None,
    "lineId": None,
    "tmnlId": None,
    "meterId": None,
    "serialNo": None,
    "groupIds": [20930000000],
    "rawType": "06",
    "rangePicker": None,
    "startTime": "2025-06-01 00:00:00",
    "endTime": "2025-07-30 23:59:59",
    "meterIds": [
        14213,
        96081,
    ],
    "defaultGroup": "__93%",
    "ntmnlTypeCode": "02",
}


@pytest.fixture(scope="module")
def random_org(pg_connect):
    cur = pg_connect.cursor()
    multiple_org_sql = """
    (select org_no from sa.sys_org so where so.org_no like %s order by random() limit 2)
    union all 
    (select org_no from sa.sys_org so where so.p_org_no is null order by random() limit 2)
    """
    cur.execute(multiple_org_sql, ("100%",))
    tables = cur.fetchall()
    orgs = [row[0] for row in tables]
    return orgs


@pytest.fixture(scope="module")
def meters(pg_connect):
    cur = pg_connect.cursor()
    multiple_device_sql = "select cm.meter_id from c_meter cm  where cm.is_delete='01' order by random() limit 1000"
    cur.execute(multiple_device_sql)
    tables = cur.fetchall()
    devices = [int(row[0]) for row in tables]
    return random.sample(devices, random.randint(2, len(devices)))


@pytest.fixture(scope="module")
def tmnls(pg_connect):
    cur = pg_connect.cursor()
    multiple_device_sql = "select rtr.tmnl_id from r_tmnl_run rtr  where rtr.is_delete='01' order by random() limit 1000"
    cur.execute(multiple_device_sql)
    tables = cur.fetchall()
    devices = [int(row[0]) for row in tables]
    return random.sample(devices, random.randint(2, len(devices)))


@pytest.fixture(scope="module")
def random_profile(api_client):
    url = "/api/profile/profileType"
    response = api_client.post(url, json={})
    if response.json()["httpStatus"] == 200:
        jsonpath_expr = parse("$..groupId")
        profile = [match.value for match in jsonpath_expr.find(response.json())]
    return random.sample(profile, random.randint(2, len(profile)))


@pytest.fixture(scope="module")
def random_time_range():
    start, end = timerange(min_duration_hours=144, max_duration_hours=1680)
    start = start.strftime("%Y-%m-%d %H:%M:%S")
    end = end.strftime("%Y-%m-%d %H:%M:%S")
    return start, end


@allure.feature("profile function")
@allure.story(
    "profile list mapping device,get protocol base device and filter profile data"
)
@allure.title("Profile Data")
@allure.severity(allure.severity_level.CRITICAL)
def test_find_profile_data_extends_field(
    meters, tmnls, random_org, random_profile, random_time_range, api_client
):
    url = "/api/profile/profileLog/page"
    for org in random_org:
        for profile in random_profile:
            template["orgNo"] = org
            template["meterIds"] = None
            template["tmnlIds"] = None
            template["groupIds"] = [profile]
            template["startTime"] = random_time_range[0]
            template["endTime"] = random_time_range[1]

            with allure.step("profile all data"):
                allure.attach(
                    body=json.dumps(template, indent=2, ensure_ascii=False),
                    name="all",
                    attachment_type=allure.attachment_type.JSON,
                )

            response = api_client.post(url, json=template)

            with allure.step("profile all response," + str(profile)):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name="all",
                    attachment_type=allure.attachment_type.JSON,
                )
            with check:
                assert response.json()["httpStatus"] == 200 or (
                    response.json()["httpStatus"] == 500
                    and response.json()["messageCode"] == "38007"
                )

            template["meterIds"] = meters
            with allure.step("profile meters data"):
                allure.attach(
                    body=json.dumps(template, indent=2, ensure_ascii=False),
                    name="meter",
                    attachment_type=allure.attachment_type.JSON,
                )

            response = api_client.post(url, json=template)

            with allure.step("profile meters response," + str(profile)):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name="meter",
                    attachment_type=allure.attachment_type.JSON,
                )
            with check:
                assert response.json()["httpStatus"] == 200 or (
                    response.json()["httpStatus"] == 500
                    and response.json()["messageCode"] == "38007"
                )

            template["tmnlIds"] = meters
            template["meterIds"] = None

            with allure.step("profile tmnl data"):
                allure.attach(
                    body=json.dumps(template, indent=2, ensure_ascii=False),
                    name="tmnl",
                    attachment_type=allure.attachment_type.JSON,
                )
            response = api_client.post(url, json=template)
            with allure.step("profile tmnl response," + str(profile)):
                allure.attach(
                    body=json.dumps(response.json(), indent=2, ensure_ascii=False),
                    name="tmnl",
                    attachment_type=allure.attachment_type.JSON,
                )
            with check:
                assert response.json()["httpStatus"] == 200 or (
                    response.json()["httpStatus"] == 500
                    and response.json()["messageCode"] == "38007"
                )
