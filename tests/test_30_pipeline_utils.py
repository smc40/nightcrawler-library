from datetime import datetime, timedelta
import requests
import sqlalchemy as sa
from libnightcrawler.db.schema import Offer, Keyword, Case


def gen_data(to_be_processed, suffix, images=None):
    if not images:
        images = []
    return [
        x.new_result(
            url="xxx_" + str(i),
            text=suffix,
            root="",
            uid="xxx_" + str(i),
            platform="",
            source="",
            title="stg",
            language="",
            score=0,
            relevant=True,
            images=images
        )
        for i, x in enumerate(to_be_processed)
    ]



def test_pipeline_utils(context, public_image, case_id):
    to_be_processed = context.get_crawl_requests()
    assert len(to_be_processed) == 2

    # Check case_id filtering
    assert len( context.get_crawl_requests(case_id=case_id+1)) == 1

    # Clear offers table
    session = context.db_client.session_factory()
    session.query(Offer).delete()
    session.commit()

    # Check empty
    assert len(session.query(Offer).all()) == 0

    # Store results
    data = gen_data(to_be_processed, "1")
    context.store_results(data, to_be_processed[0].case_id, to_be_processed[0].keyword_id)

    # Check not empty anymore
    assert len(session.query(Offer).all()) == 2

    # Check status switch to SUCCEEDED
    assert session.query(Keyword).where(Keyword.id == to_be_processed[0].keyword_id).one().crawl_state == Keyword.CrawlState.SUCCEEDED

    # Check results replaced instead of addition
    data = gen_data(to_be_processed, "2", [public_image])
    context.store_results(data, 0)
    offers = session.query(Offer).all()
    assert len(offers) == 2

    images_config = offers[0].images
    for config in images_config:
        assert config["source"] == public_image
        assert context.blob_client.get_image(config["path"]) == requests.get(public_image).content

    request = to_be_processed[0]
    error = "some string"
    context.set_crawl_error(request.case_id, request.keyword_id, error)
    keyword = session.query(Keyword).where(Keyword.id == request.keyword_id).one()
    assert keyword.crawl_state == Keyword.CrawlState.FAILED
    assert keyword.error == error

def _change_dates(session, case_id, start, end):
    stmt = (
                sa.update(Case)
                .where(Case.id == case_id)
                .values(start_date=start, end_date=end)
            )
    session.execute(stmt)
    session.commit()

def test_case_expiration(context, public_image, case_id):
    assert len(context.get_crawl_requests()) == 2

    session = context.db_client.session_factory()
    today = datetime.now().date()
    _change_dates(session, case_id, today, today - timedelta(days=1))

    assert len(context.get_crawl_requests()) == 0

    _change_dates(session, case_id, today, today)
    assert len(context.get_crawl_requests()) == 2
