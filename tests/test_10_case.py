from libnightcrawler.db.schema import Case, Keyword


def test_case(context, org_id, case_id):
    session = context.db_client.session_factory()
    
    # Clear previous state
    session.query(Case).delete()
    session.query(Keyword).delete()

    # Add 1 active and 1 inactive case
    session.add(Case(org_id=org_id, id=case_id, name="test"))
    session.add(Case(org_id=org_id, id=case_id + 1, name="test2", inactive=True))

    # Add Keywords to active case
    session.add(Keyword(case_id=case_id, query="testquery", type=Keyword.KeywordType.TEXT, crawl_state=Keyword.CrawlState.PENDING))
    session.add(Keyword(case_id=case_id, query="banana", type=Keyword.KeywordType.TEXT, crawl_state=Keyword.CrawlState.PENDING))

    # Add Keyword to inactive case
    session.add(Keyword(case_id=case_id+1, query="testquery2", type=Keyword.KeywordType.TEXT, crawl_state=Keyword.CrawlState.PENDING))

    session.commit()
