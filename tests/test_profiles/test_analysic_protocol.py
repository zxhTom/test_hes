import pytest
import allure
import json
from jsonpath_rw import parse
from utils.check_utils import check
import random

from collections import defaultdict

import jmespath

protocol_list_sql = """
		SELECT
		distinct (p_obis.obis_id),
		p_obis.protocol_id,
		p_obis.obis_no,
		p_obis.class_id,
		p_obis.attribute_method_id,
		p_obis.data_format,
		p_obis.data_length,
		p_obis.ratio,
		p_obis.obis_name,
		p_obis.obis_name_cin,
		p_obis.attrbute_method_name,
		p_obis.meter_type,
		p_obis.belong_to_function,
		p_obis.category1,
		p_obis.category2,
		p_obis.isproductionline,
		p_obis.ispclocal,
		p_obis.isahe,
		p_obis.remarks,
		p_obis.is_visible,
		p_obis.main_cat,
		p_obis.access_perms,
		p_obis.sql_id,
		p_obis.fun_cat,
		p_obis.main_cat_order,
		p_obis.content_type,
		p_obis.value_range,
		p_obis.need_cap,
		p_obis.get_buffer,
		p_obis.main_cat_chiness,
		p_obis.data_format,
		TRIM(p_obis.access_perms) AS accessPerms, p_obis.protocol_id AS protId,
		p_obis.attribute_method_id AS attrIdx,
		p_obis.data_length AS dataLen,
		sgct.object_type,sgct.code_table_name
		FROM p_obis
		INNER JOIN p_obis_group og ON og.obis_id = p_obis.obis_id
		INNER JOIN p_group g ON g.group_id = og.group_id
		LEFT JOIN sys_group_code_table sgct ON  g.group_id = sgct.group_id

"""

# protocolId, classId, obisNo, attrIdx


# p_xml_attribute{}
def replace_third_after_split(s):
    """按下划线分隔，将第三部分替换为*号"""
    parts = s.split("_")
    if len(parts) >= 3:
        parts[2] = "*"  # 将第三部分替换为*
    return "_".join(parts)


def list_to_map_defaultdict(item_list):
    """使用defaultdict自动创建列表"""
    result_map = defaultdict(list)
    for item in item_list:
        key = replace_third_after_split(item)
        result_map[key].append(item)
    return dict(result_map)  # 转换为普通dict


def replace_digit_sequences(s, max_digit=9, suffix="d"):
    """自动替换 /1 到 /max_digit 的序列"""
    result = s
    for i in range(1, max_digit + 1):
        pattern = rf"/{i}"
        replacement = f"{i}{suffix}"
        result = result.replace(pattern, replacement)
    return result


@allure.feature("batch check protocol configuratioin")
@allure.story("check front backend weather their configuration error")
@allure.title("protocol data")
@allure.severity(allure.severity_level.CRITICAL)
def test_find_protocol_configuration_data(api_client, pg_connect):
    cur = pg_connect.cursor()
    cur.execute(protocol_list_sql)
    tables = cur.fetchall()
    keys = [
        f"{row[1]}_{row[3]}_{row[2]}_{replace_digit_sequences(row[4])}"
        for row in tables
    ]
    exists_sql = "select concat(pxa.protocol_id,'_',pxa.obis_id) from p_xml_attribute pxa where concat(pxa.protocol_id,'_',pxa.obis_id)=ANY(%s)"
    cur.execute(exists_sql, (keys,))
    right_protocols = [row[0] for row in cur.fetchall()]
    print(len(keys))
    print(len(right_protocols))
    diff = [replace_third_after_split(x) for x in keys if x not in right_protocols]
    diffMapList = list_to_map_defaultdict([x for x in keys if x not in right_protocols])
    cur.execute(exists_sql, (diff,))
    last_right_protocols = [row[0] for row in cur.fetchall()]
    last_diff = [x for x in diff if x not in last_right_protocols]
    datas = []
    for item in last_diff:
        datas.append(diffMapList[item])

    with allure.step("error protocol configuration"):
        allure.attach(
            body=json.dumps(datas, indent=2, ensure_ascii=False),
            name="out",
            attachment_type=allure.attachment_type.JSON,
        )
    with check:
        assert len(datas) == 0
