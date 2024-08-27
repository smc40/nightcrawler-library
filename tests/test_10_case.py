from libnightcrawler.db.schema import Case


def test_case(context, tenant_id, case_id):
    session = context.db_client.session_factory()
    session.query(Case).delete()
    session.add(Case(tenant_id=tenant_id, id=case_id, name="test"))
    session.commit()
