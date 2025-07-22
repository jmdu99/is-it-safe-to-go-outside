import requests

def test_suggest_fields(base_url, session_token):
    resp = requests.get(
        f"{base_url}/suggest",
        params={"q": "Le Wagon Paris", "session_token": session_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert set(item.keys()) == {"id", "name", "full_address", "place_formatted"}
        assert isinstance(item["id"], str)
        assert isinstance(item["name"], str)
        assert item["full_address"] is None or isinstance(item["full_address"], str)
        assert isinstance(item["place_formatted"], str)

def test_retrieve_fields(base_url, session_token):
    suggest = requests.get(
        f"{base_url}/suggest",
        params={"q": "Paris", "session_token": session_token},
    ).json()
    first_id = suggest[0]["id"]
    resp = requests.get(
        f"{base_url}/retrieve/{first_id}",
        params={"session_token": session_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {
        "id", "name", "full_address", "place_formatted", "center"
    }
    assert isinstance(data["id"], str)
    assert isinstance(data["name"], str)
    assert data["full_address"] is None or isinstance(data["full_address"], str)
    assert isinstance(data["place_formatted"], str)
    assert isinstance(data["center"], list) and len(data["center"]) == 2
    assert all(isinstance(c, (int, float)) for c in data["center"])

def _check_risk_structure(data):
    assert set(data.keys()) == {
        "location", "risk_index", "risk_label", "weather", "pollution", "norm"
    }
    loc = data["location"]
    assert set(loc.keys()) == {"latitude", "longitude"}
    assert isinstance(loc["latitude"], (int, float))
    assert isinstance(loc["longitude"], (int, float))
    assert isinstance(data["risk_index"], float)
    assert isinstance(data["risk_label"], str)
    for section in ("weather", "pollution", "norm"):
        assert isinstance(data[section], dict)

def test_risk_query_fields(base_url, session_token):
    resp = requests.get(
        f"{base_url}/risk",
        params={"query": "Paris", "session_token": session_token},
    )
    assert resp.status_code == 200
    _check_risk_structure(resp.json())

def test_risk_mapbox_id_fields(base_url, session_token):
    suggest = requests.get(
        f"{base_url}/suggest",
        params={"q": "Paris", "session_token": session_token},
    ).json()
    first_id = suggest[0]["id"]
    resp = requests.get(
        f"{base_url}/risk",
        params={"mapbox_id": first_id, "session_token": session_token},
    )
    assert resp.status_code == 200
    _check_risk_structure(resp.json())
