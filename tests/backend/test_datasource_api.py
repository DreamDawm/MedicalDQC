def test_create_datasource(client):
    response = client.post("/api/datasources", json={
        "name": "test-db",
        "db_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "testdb",
        "username": "user",
        "password": "pass",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-db"
    assert data["db_type"] == "postgresql"
    assert "id" in data


def test_list_datasources(client):
    client.post("/api/datasources", json={
        "name": "ds1",
        "db_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "db1",
        "username": "user",
        "password": "pass",
    })
    response = client.get("/api/datasources")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_datasource(client):
    res = client.post("/api/datasources", json={
        "name": "to-delete",
        "db_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "database": "db1",
        "username": "user",
        "password": "pass",
    })
    ds_id = res.json()["id"]
    del_res = client.delete(f"/api/datasources/{ds_id}")
    assert del_res.status_code == 200
    list_res = client.get("/api/datasources")
    assert len(list_res.json()) == 0
