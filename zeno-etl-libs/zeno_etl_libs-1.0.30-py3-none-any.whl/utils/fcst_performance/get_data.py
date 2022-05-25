from datetime import timedelta


class GetData:
    """To fetch required data from SQL and PostGre"""
    def __init__(self, store_ids, reset_date, days_to_replenish, days_delta,
                 db, schema, logger):
        """
        Arguments:
            store_ids: (list) store id list
            reset_date: (datetime.date) format
            days_to_replenish: (int) days to skip for inventory replenishment
            from date of reset
        """
        self.store_ids = str(store_ids).replace('[', '(').replace(']', ')')
        self.reset_date = reset_date.strftime('%Y-%m-%d')
        self.date_before_90days = (reset_date - timedelta(90)).strftime('%Y-%m-%d')
        self.start_date = (reset_date + timedelta(days_to_replenish)).strftime('%Y-%m-%d')
        self.end_date = (reset_date + timedelta(days_to_replenish+days_delta-1)).strftime('%Y-%m-%d')
        # considering sales period of 28 days (start & end date included in sql)
        self.db = db
        self.schema = schema
        self.logger = logger

    def ipc_ss(self, store_id, sql_cut_off_condition):
        """Fetch safety stock table for current IPC store and reset date"""
        self.logger.info(f"Fetching ipc_ss data for store_id: {store_id}")
        q_ss = """
            select *
            from "{schema}"."ipc-safety-stock" 
            where "store-id" = {0} and "reset-date" = '{1}'
            {2}
            """.format(store_id, self.reset_date, sql_cut_off_condition,
                       schema=self.schema)
        df_ss = self.db.get_df(q_ss)
        df_ss.columns = [c.replace('-', '_') for c in df_ss.columns]
        df_ss["store_type"] = "ipc"
        return df_ss

    def non_ipc_ss(self, store_id, sql_cut_off_condition):
        """Fetch safety stock table for current Non-IPC store and reset date"""
        self.logger.info(f"Fetching non_ipc_ss data for store_id: {store_id}")
        q_ss = """
            select *
            from "{schema}"."non-ipc-safety-stock"
            where "store-id" = {0} and "reset-date" = '{1}'
            {2}
            """.format(store_id, self.reset_date, sql_cut_off_condition,
                       schema=self.schema)
        df_ss = self.db.get_df(q_ss)
        df_ss.columns = [c.replace('-', '_') for c in df_ss.columns]
        df_ss["store_type"] = "non_ipc"
        return df_ss

    def curr_inv(self):
        """Fetch current inventory for all stores"""
        self.logger.info("Fetching inventory data")
        q_inv = """
            SELECT "drug-id" as drug_id, 
            "store-id" as store_id, 
            AVG(ptr) AS average_ptr, 
            SUM("locked-quantity"+quantity+"locked-for-audit"+"locked-for-transfer" 
            +"locked-for-check"+"locked-for-return") AS current_inventory 
            FROM "{schema}"."inventory-1" 
            WHERE "store-id" in {0}
            GROUP BY "store-id", "drug-id"
            """.format(self.store_ids, schema=self.schema)
        df_inv_comb = self.db.get_df(q_inv)
        return df_inv_comb

    def sales_3m(self):
        """Fetch last 3 months sales data for finding weather NPI or not."""
        self.logger.info("Fetching 3 months sales data")
        q_3m_sales = """
            select 
            "drug-id", "store-id",
            sum("net-quantity") as "net-sales-3m"
            from "{schema}".sales
            where "store-id" in {0} and
            date("created-at") between '{1}' and '{2}'
            group by "store-id", "drug-id"
            """.format(self.store_ids, self.date_before_90days, self.reset_date,
                       schema=self.schema)
        df_3m_sales_comb = self.db.get_df(q_3m_sales)
        df_3m_sales_comb.columns = [c.replace('-', '_') for c in df_3m_sales_comb.columns]
        return df_3m_sales_comb

    def sales_28day(self):
        """Fetch 28 days sales data after date of reset"""
        self.logger.info("Fetching 28 days sales data")
        q_sales = """
            select 
            "drug-id", "store-id",
            sum("net-quantity") as "net-sales"
            from "{schema}".sales
            where "store-id" in {0} and
            date("created-at") between '{1}' and '{2}'
            group by "store-id", "drug-id"
            """.format(self.store_ids, self.start_date, self.end_date,
                       schema=self.schema)
        df_sales_comb = self.db.get_df(q_sales)
        df_sales_comb.columns = [c.replace('-', '_') for c in df_sales_comb.columns]
        return df_sales_comb

    def pr_loss_28day(self):
        """Fetch 28 days PR losses after date of reset"""
        self.logger.info("Fetching 28 days pr loss data")
        q_pr = """
            select "drug-id", "store-id",
            sum("loss-quantity") as "pr-loss"
            from "{schema}"."cfr-patient-request"
            where "shortbook-date" between '{1}' and '{2}'
            and "store-id" in {0}
            group by "store-id", "drug-id"
            """.format(self.store_ids, self.start_date, self.end_date,
                       schema=self.schema)
        df_pr_loss_comb = self.db.get_df(q_pr)
        df_pr_loss_comb.columns = [c.replace('-', '_') for c in df_pr_loss_comb.columns]
        return df_pr_loss_comb

