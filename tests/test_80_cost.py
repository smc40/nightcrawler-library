from libnightcrawler.db.schema import Cost, COST_UNIT_FACTOR


def test_cost(context, case_id):
    # clear costs table
    session = context.db_client.session_factory()
    session.query(Cost).delete()
    session.commit()

    initial = context.get_current_cost(case_id)
    assert initial == 0

    context.report_cost(case_id, 10, Cost.Unit.UNIT)
    assert context.get_current_cost(case_id) == initial + 10 * COST_UNIT_FACTOR[Cost.Unit.UNIT.value]

    # Check unit conversion
    context.report_cost(case_id, 3, Cost.Unit.ZYTE)
    expected = initial + 10 + 3 * COST_UNIT_FACTOR[Cost.Unit.ZYTE.value]
    assert context.get_current_cost(case_id) == expected

    # Add cost to another case and check it didn't change
    context.report_cost(case_id + 1, 3, Cost.Unit.ZYTE)
    assert context.get_current_cost(case_id) == expected
