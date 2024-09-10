from libnightcrawler.db.schema import Offer


def test_pipeline_utils(context):
    to_be_processed = context.get_crawl_requests()
    assert len(to_be_processed) == 2

    # Clear offers table
    session = context.db_client.session_factory()
    session.query(Offer).delete()
    session.commit()

    # Check empty
    assert len(session.query(Offer).all()) == 0

    # Store results
    data = [
        x.new_result(
            url="xxx",
            text="",
            root="",
            uid="",
            platform="",
            source="",
            title="",
            language="",
            score=0,
        )
        for x in to_be_processed
    ]
    context.store_results(data)

    # Check not empty anymore
    assert len(session.query(Offer).all()) == 2
