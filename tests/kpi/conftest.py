import pytest


@pytest.fixture
def generate_test_pairs(pg_connect):
    res = []
    cur = pg_connect.cursor()
    multiple_org_sql = "select org_no from sa.sys_org so where so.org_no like %s order by random() limit 2"
    cur.execute(multiple_org_sql, ("100%",))
    tables = cur.fetchall()
    for table in tables:
        item = {
            "orgNo": str(table[0]),
            "lineIds": [],
            "tranIds": [],
            "substationIds": [],
            "deviceType": "01",
        }
        res.append(item)
    return res
