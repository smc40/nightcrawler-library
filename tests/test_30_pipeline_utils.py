from libnightcrawler.db.schema import Offer


def gen_data(to_be_processed, suffix):
    return [
        x.new_result(
            url="xxx_" + str(i),
            text=suffix,
            root="",
            uid="",
            platform="",
            source="",
            title="",
            language="",
            score=0,
            relevant=True
        )
        for i, x in enumerate(to_be_processed)
    ]



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
    data = gen_data(to_be_processed, "1")
    context.store_results(data)

    # Check not empty anymore
    assert len(session.query(Offer).all()) == 2

    # Check results replaced instead of addition
    data = gen_data(to_be_processed, "2")
    context.store_results(data)
    assert len(session.query(Offer).all()) == 2
