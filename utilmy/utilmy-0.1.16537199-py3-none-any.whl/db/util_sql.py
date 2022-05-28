"""# 
Doc::

List of SQL

## #1: MoM Percent Change 
**Context:** Often times it's useful to know how much a key metric, 
such as monthly active users, changes between months. Say we have a table `logins` in the form: 

| user_id | date       |
|---------|------------|
| 1       | 2018-07-01 |
| 234     | 2018-07-02 |
| 1       | 2018-07-02 |
| ...     | ...        |
| 234     | 2018-10-04 |
**Task**: Find the month-over-month percentage change for monthly active users (MAU). 
***Solution:***


#### solution OK 
SELECT  tyear, tmonth,  (n_user / lag(n_user,1) -1.0)*100.0   as mau_pct_chg
FROM (
select tyear, tmonth  count(user_id) as n_user

FROM  (
  Select   year(date) as tyear, month(date) as tmonth, user_id
  from users as t1
)
 group by year,month
 ORDER BY year, month
)


#### Solution with n_users = 0 for some months
#### generate the 12 month ??? manually, how you would do ?
(
  SELECT YEAR(a.my_date) AS my_year, MONTH(a.my_date) AS my_month 
  FROM
  (
    SELECT curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) MONTH as my_date
    FROM (
          select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as a
    
          CROSS JOIN (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as b
     
          CROSS JOIN (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as c

  ) a









## #2: Tree Structure Labeling   
**Context:** Say you have a table `tree` with a column of nodes and a column corresponding parent nodes 

```
node   parent
1       2
2       5
3       5
4       3
5       NULL 
```

**Task:** Write SQL such that we label each node as a “leaf”, “inner” or “Root” node, such that for the nodes above we get: 

```
node    label  
1       Leaf
2       Inner
3       Inner
4       Leaf
5       Root
```

(Side note: [this link](http://ceadserv1.nku.edu/longa//classes/mat385_resources/docs/trees.html) has more details on Tree data structure terminology. Not needed to solve the problem though!)
* * *
***Solution:***





























## #3: Retained Users Per Month (multi-part)
** [“Using Self Joins to Calculate Your Retention, Churn, and Reactivation Metrics”]
(https://www.sisense.com/blog/use-self-joins-to-calculate-your-retention-churn-and-reactivation-metrics/) 
### Part 1: 
**Context:** Say we have login data in the table `logins`: 
| user_id | date       |
|---------|------------|
| 1       | 2018-07-01 |
| 234     | 2018-07-02 |
| 1       | 2018-07-02 |
| ...     | ...        |
| 234     | 2018-10-04 |
**Task:** Write a query that gets the number of retained users per month. In this case, retention for a given month is defined as the number of users who logged in that month who also logged in the immediately previous month. 

***Solution:***  
1)  pelase confirm if my code is OK or not ( correct or NOT) - yes, looks good
WITH  monthly_users
AS(       
             select tyear, tmonth, tyear_prev, tmonth_prev  count(user_id) as n_user
FROM  (
  Select   year(date) as tyear, month(date) as tmonth, user_id,
               year(add_month(date, -1))    as   tyear_prev,    ### added prev month here using add_month
               month(add_month(date, -1)) as   tmonth_prev             
  from users as t1
)
 group by tyear, tmonth, tyear_prev, tmonth_prev
 ORDER BY tyear, tmonth, tyear_prev, tmonth_prev
) ,

SELECT  tyear, tmonth, n_user
FROM      monthly_users as t1
INNER JOIN (  -- user in both months
   SELECT * FROM monthly_users
) as t2 
ON       
    t2.user_id          =  t1.user_id
    AND  t2.year     =  t1.year_prev   ### previous month
    AND  t2.month  =  t1.month_prev
  

2nd) (ie more optimized)
Part1: retained
WITH monrhtly_user AS
(
    
)
Select
	tyear, tmonth, count(u.user_id) AS n_user
From monthly_users AS t1
INNER Join monthly_users AS t2   
   ON   t1.user_id = t2.user_id 
   AND CAST(month(t1.date) as INT) = cast(month(DATEADD(month, -1, t1.date)) as INT) 
   AND CAST(year(t1.date)  as INT) = cast(year(DATEADD(month, -1, t1.date))  as INT) 
 
  
With dateadd you don’t need to separate year and month
Be careful to consider multi-year data, or generic case in your solutions,
Ok, it;sa similar to my solution with date operator on the condition + dateadd
Using datediff



### Part 2: 
**Task:** Now we’ll take retention and turn it on its head: Write a query to find how many users last month *did not* come back this month. i.e. the number of churned users.  
***Solution:***

SELECT   tyear, tmonth, count(user_id)
FROM       users t1                 ###   (Previous month)

LEFT JOIN users   AS t2       ###   Next month
ON   
   t2.user_id = t1.user_id
   AND  MONTH( t2.date) =  MONTH( dateadd(month, +1,  t1.date   )
   AND  YEAR(  t2.date)   =  YEAR( dateadd(month,  +1,    t1.date   )
WHERE
        t2.user_id IS NULL

GROUP BY tyear, tmonth


trick:         LEFT JOIN    t2.user_id is NULL       ===  user_id NOT IN (  Select user_id ...)
Dont always limit just to the text description (ie  natural Genealization is better,  more practice == real world thing,)



### Part 3: 
**Note:** this question is probably more complex Consider it a challenge problem

**Context**: Data engineering has decided to give you a helping hand by creating a table of churned users per month, `user_churns`. If a user is active last month but then not active this month, then that user gets an entry for this month. `user_churns` has the form: 
| user_id | month_date |
|---------|------------|
| 1       | 2018-05-01 |
| 234     | 2018-05-01 |
| 3       | 2018-05-01 |
| 12      | 2018-05-01 |
| ...     | ...        |
| 234     | 2018-10-01 |
```

**Task**: You now want to do a cohort analysis of active users this month *who have been reactivated users in the past*. Create a table that contains these users. You may use the tables `user_churns` as well as `logins` to create this cohort. In Postgres, the current timestamp is available through `current_timestamp`.
* * *
***Solution:***



















## #4: Cumulative Sums 
Cash Flow modeling in SQL”](https://www.sisense.com/blog/cash-flow-modeling-in-sql/)t 

**Context:** Say we have a table `transactions` in the form:
| date       | cash_flow |
|------------|-----------|
| 2018-01-01 | -1000     |
| 2018-01-02 | -100      |
| 2018-01-03 | 50        |
| ...        | ...       |
```
Where `cash_flow` is the revenues minus costs for each day. 

**Task: **Write a query to get *cumulative* cash flow for each day such that we end up with a table in the form below: 
| date       | cumulative_cf |
|------------|---------------|
| 2018-01-01 | -1000         |
| 2018-01-02 | -1100         |
| 2018-01-03 | -1050         |
| ...        | ...           |
***Solution:***  http://sqlfiddle.com/#!18/abdce/1
Below is correct ???






#### using Self-JOIN
with cf_table AS     ### 1 cashflow per date
select date, sum(cash_flow) as cf    
from      cash_flows as t1
GROUP BY date
ORDER by date
,
SELECT t1.date,  sum(t2.cf) as cumulateive_cf  
FROM cf_table as t1

INNER JOIN (
       Select   *  FROM cf_table
      )  AS t2 
    ON  t2.date <= t1.date   ##  OK: sum of previous days
GROUP BY t1.date   
 

#### Solution by Yvan
SELECT 
t.date [date], 
SUM(tt.cash_flow) as cumulative_cf 
FROM transactions t1
INNER JOIN transactions t2 
    ON t2.date  <=    t1.date   ### only past dates 
GROUP BY t.date 
ORDER BY t.date ASC
   
It;s more logical to  use   <=      ie previous date sum.  :  Cum sum of past dates. !!!
   









## #5: Rolling Averages
”(https://www.sisense.com/blog/rolling-average/) blog post 
**Note:** there are different ways to compute rolling/moving averages. Here we'll use a preceding average which means that the metric for the 7th day of the month would be the average of the preceding 6 days and that day itself. 
**Context**: Say we have table `signups` in the form: 
| date       | sign_ups |
|------------|----------|
| 2018-01-01 | 10       |
| 2018-01-02 | 20       |
| 2018-01-03 | 50       |
| ...        | ...      |
| 2018-10-01 | 35       |
**Task**: Write a query to get 7-day rolling (preceding) average of daily sign ups. 


#### Solution 1
SELECT 
t1.date, 
AVG(t2.sign_ups) average_sign_ups 
FROM signups AS t1
INNER JOIN signups AS t2 
      ON   t1.date   >=  dateadd(day, -6, t2.date)  ## preceding 6 days
      AND  t1.date   <=  t2.date                    ## that day itself. 
GROUP BY t1.date

### ok. it;s generic way to write moving average.
Matchin Descpriotn parameters   :    preceding 6 days
== more intuitive, easier to cross check



### Solution using windowing ( in Hive SQL), OK
select date
          ,AVG(sign_ups)  OVER (  ORDER BY date  
                                                   ROWS BETWEEN  6 PRECEDING AND CURRENT ROW) ### not familiar with this syntax, for pseudocode OK
          as signup_avg_7day
FROM table t1

### With Missing days:
          ,AVG(sign_ups)  OVER (  ORDER BY date  
                                                    RANGE BETWEEN  6 PRECEDING AND CURRENT ROW)
























"""




