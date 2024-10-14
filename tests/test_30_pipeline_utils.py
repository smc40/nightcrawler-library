import requests
from libnightcrawler.db.schema import Offer, Keyword


def gen_data(to_be_processed, suffix, images=None):
    if not images:
        images = []
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
            relevant=True,
            images=images
        )
        for i, x in enumerate(to_be_processed)
    ]



def test_pipeline_utils(context, public_image):
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
    context.store_results(data, to_be_processed[0].keyword_id)

    # Check not empty anymore
    assert len(session.query(Offer).all()) == 2

    # Check status switch to SUCCEEDED
    assert session.query(Keyword).where(Keyword.id == to_be_processed[0].keyword_id).one().crawl_state == Keyword.CrawlState.SUCCEEDED

    # Check results replaced instead of addition
    data = gen_data(to_be_processed, "2", [public_image])
    context.store_results(data)
    offers = session.query(Offer).all()
    assert len(offers) == 2

    images_config = offers[0].images
    for config in images_config:
        assert config["source"] == public_image
        assert context.blob_client.get_image(config["path"]) == requests.get(public_image).content
