def test_get_system_configuration(api_client, env_config):
    """测试创建用户接口"""
    payload = {"moduleName": "system"}

    response = api_client.post("/api/users/systemParamters", json=payload)
    print(response.json())
    if response.status_code == 409:  # 用户名已存在
        pytest.skip("用户已存在，跳过创建测试")
    else:
        assert (
            response.status_code == 200 and response.json()["httpStatus"] == 200
        ), response.text
