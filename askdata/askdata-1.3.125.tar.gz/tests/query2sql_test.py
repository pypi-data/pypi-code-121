from askdata import human2query
from askdata.smartquery import SmartQuery, Query, Field, Condition, Sorting, SQLSorting, SQLOperator, TimeOperator, \
    BooleanOperator, CompositeCondition

if __name__ == "__main__":

    # Query2SQL
    smartquery = SmartQuery(
        queries=[
            Query(
                fields=[
                    Field(aggregation="SUM", column="incidents", alias="sum_incidents",
                          internalDataType="NUMERIC",
                          sourceDataType="INT64"),
                    Field(column="customer_name", alias="Customer",
                          internalDataType="STRING",
                          sourceDataType="VARCHAR"),
                    Field(aggregation="YEAR", column="acquired", alias="Acquired Date",
                          internalDataType="DATE",
                          sourceDataType="DATE")
                ],
                where=[
                    CompositeCondition(conditions=[
                        Condition(field=Field(column="customer_name", alias="Customer",
                                              internalDataType="STRING",
                                              sourceDataType="VARCHAR"), operator=SQLOperator.IN,
                                  value=["Franceaco Doe", "Claude Rudolf"]),
                        Condition(field=Field(aggregation="YEAR", column="acquired", alias="Acquired Date",
                                              internalDataType="DATE",
                                              sourceDataType="DATE"), operator=TimeOperator.RANGE,
                                  value=["2018-01-01", "2019-12-31"])
                    ], operator=BooleanOperator.AND)

                ],
                orderBy=[
                    Sorting(field="Acquired Date", order=SQLSorting.DESC)
                ],
                limit=6
            )
        ]
    )

    response = human2query.query2sql(smartquery=smartquery, driver="MySQL")
    print(response)
    response = human2query.complex_field_calculator(smartquery=smartquery, driver="MySQL")
    print(response)
    response = human2query.complex_filter_calculator(smartquery=smartquery, driver="MySQL")
    print(response)
