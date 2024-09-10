
def test_organization(context):
    data = context.get_organization()
    assert len(data.keys()) == 3
    assert data["Swissmedic MEP"].unit == "mep"
    assert len(data["Swissmedic MEP"].blacklist) > 0
    assert data["Swissmedic AM"].unit == "am"
    assert len(data["Swissmedic AM"].blacklist) > 0
    assert data["Ages"].countries == ["at"]
    assert len(data["Ages"].blacklist) == 0
