def migrate(cr, version):
    cr.execute(
        "DELETE FROM mail_tracking_value mtv USING mail_message mm "
        "WHERE mtv.mail_message_id = mm.id AND mm.model='contract.contract' AND "
        "EXTRACT(hour FROM new_value_datetime) > 22 AND "
        "field IN ('write_date','__last_update') AND mm.create_date>'2021-12-02'"
    )
    cr.execute(
        "DELETE FROM mail_message WHERE create_date>'2021-12-02' AND "
        "EXTRACT(hour FROM create_date) > 22 AND model='contract.contract'"
    )
