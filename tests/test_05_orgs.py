
def _check_org(data):
    assert len(data.keys()) == 3
    assert data["Swissmedic MEP"].unit == "mep"
    assert len(data["Swissmedic MEP"].blacklist) > 0
    assert data["Swissmedic AM"].unit == "am"
    assert len(data["Swissmedic AM"].blacklist) > 0
    assert len(data["Ages"].blacklist) == 0


def test_organization_db(context):
    data = context.get_organization()
    _check_org(data)
