def test_simple_select(db_cursor):
    db_cursor.execute("select 1")
    res = db_cursor.fetchone()
    assert res == (1,)
