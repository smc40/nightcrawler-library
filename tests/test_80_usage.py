from libnightcrawler.db.schema import Usage, USAGE_UNIT_FACTOR


def test_usage(context, case_id):
    # clear usages table
    session = context.db_client.session_factory()
    session.query(Usage).delete()
    session.commit()

    initial = context.get_current_usage(case_id)
    assert initial == 0

    context.report_usage(case_id, {Usage.Unit.UNIT.value: 10})
    assert context.get_current_usage(case_id) == initial + 10 * USAGE_UNIT_FACTOR[Usage.Unit.UNIT.value]

    # Check unit conversion
    context.report_usage(case_id, {Usage.Unit.ZYTE.value: 3})
    expected = initial + 10 + 3 * USAGE_UNIT_FACTOR[Usage.Unit.ZYTE.value]
    assert context.get_current_usage(case_id) == expected

    # Add usage to another case and check it didn't change
    context.report_usage(case_id + 1, {Usage.Unit.ZYTE.value: 3})
    assert context.get_current_usage(case_id) == expected
