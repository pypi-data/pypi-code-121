# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import hbshare as hbs
import warnings
warnings.filterwarnings('ignore', category=pymysql.Warning)


class HBDB:
    def __init__(self):
        hbs.set_token("")

    def get_df(self, sql, db, page_size=2000):
        data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
        pages = data['pages']
        data = pd.DataFrame(data['data'])
        if pages > 1:
            for page in range(2, pages + 1):
                temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
                data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
        return data

    def read_report_date(self):
        sql = "select distinct(jsrq) as REPORT_DATE FROM st_fund.t_st_gm_gpzh"
        df = self.get_df(sql, db='funduser')
        return df

    def read_cal(self, start, end):
        sql = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ>={0} and JYRQ<={1}".format(start, end)
        df = self.get_df(sql, db='readonly')
        return df

    def read_stock_fund_info(self):
        sql = "select jjdm, jjmc, jjjc, clrq, zzrq, ejfl, kffb from st_fund.t_st_gm_jjxx where jjzt='0' and cpfl='2' and ejfl in ('13', '35', '37')"
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_company_given_code(self, code):
        sql = "select jjdm, jgdm, jgmc from funddb.JJGL where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='readonly')
        return df

    def read_fund_manager_given_code(self, code):
        sql = "select jjdm, rydm, ryxm, ryzw, bdrq, ryzt, rzrq, lrrq, lryy from st_fund.t_st_gm_jjjl where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_target_given_code(self, code):
        sql = "select jjdm, tzmb from funddb.JJXX2 where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='readonly')
        return df

    def read_fund_scale_given_code(self, code):
        sql = "select jjdm, bblb1, jsrq, ggrq, zcjz from funddb.CWZB where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='readonly')
        return df

    def read_fund_share_given_code(self, code):
        sql = "select jjdm, bblb, jsrq, plrq, qsrq, qcfe, qjsgfe, cfzjfe, wjshfe, qmfe from st_fund.t_st_gm_febd where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_holder_given_code(self, code):
        sql = "select jjdm, jsrq, ggrq, jgcyfe, jgcybl, grcyfe, grcybl from st_fund.t_st_gm_fecyrbd where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_manager_product_given_code(self, manager_code):
        sql = "select rydm, jsrq, zgcpsl, zgcpgm, dbjj from st_fund.t_st_gm_jlzgcptj where rydm='{0}'".format(manager_code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_manager_achievement_given_code(self, manager_code, code):
        sql = "select rydm, jjdm, qsrq, jsrq, rqts, hbrq, rqnhhb, zdyl, zdhc, nhxpbl, kmbl from st_fund.t_st_gm_jlrqhb where rydm='{0}' and jjdm='{1}'".format(manager_code, code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_position_given_code(self, code):
        sql = "select jjdm, jsrq, jjzzc, gptzsz, zqzsz, jjtzszhj, hbzjsz from st_fund.t_st_gm_zcpz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_cr_given_code(self, code):
        sql = "select jjdm, jsrq, qsdzb, qsdzbtlpj, qwdzb, qwdzbtlpj from st_fund.t_st_gm_cgjzd where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_turnover_given_code(self, code):
        sql = "select jjdm, jsrq, tjqj, hsl from st_fund.t_st_gm_jjhsl where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_nav_given_code(self, code):
        sql = "select jjdm, jzrq, jjjz, ljjz from st_fund.t_st_gm_jjjz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_benchmark_nav_given_code(self, code):
        sql = "select jjdm, jzrq, jzhbdr from st_fund.t_st_gm_jzrhb where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_benchmark_given_code(self, code):
        sql = "select JJDM, BDRQ, BJJZ, SYZT from funddb.BJJZ where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='readonly')
        return df

    def read_fund_wind_size_given_code(self, code):
        sql = "select jjdm, wdszsx from st_fund.t_st_gm_jjxx where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_return_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, rqnp, zbnp, zbnhnp from st_fund.t_st_gm_rqjhb where jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_samekind_return_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, pmnpyj, slnpyj, zbnpyj, pmnpej, slnpej, zbnpej, zbnhnpyj, zbnhnpej from st_fund.t_st_gm_rqjhbpm where jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_return_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.hb1n, b.hb1npmyj, b.hb1npmej, b.hb1npmslyj, b.hb1npmslej, b.pjhb1nyj, b.pjhb1nej from st_fund.t_st_gm_nhb a left join st_fund.t_st_gm_nhbpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_volatility_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.zzbnp1n, a.znhzbnp1n, b.zbdpm1nyj, b.tlzbdsl1nyj, b.zbdpm1nej, b.tlzbdsl1nej, b.pjzbd1nyj, b.pjnhzbd1nyj, b.pjzbd1nej, b.pjnhzbd1nej from st_fund.t_st_gm_nbdl a left join st_fund.t_st_gm_nbdlpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_sharpratio_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.zzbnp1n, a.znhzbnp1n, b.zxppm1nyj, b.tlzxpsl1nyj, b.zxppm1nej, b.tlzxpsl1nej, b.pjzxp1nyj, b.pjznhxp1nyj, b.pjzxp1nej, b.pjznhxp1nej from st_fund.t_st_gm_nxpbl a left join st_fund.t_st_gm_nxpblpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_maxdrawdown_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.zbnp1n, a.zdhchfts1n, a.zdhccxts1n, b.hczdpm1nyj, b.tlhczdsl1nyj, b.hczdpm1nej, b.tlhczdsl1nej, b.pjhczd1nyj, b.pjhczd1nej from st_fund.t_st_gm_nzdhc a left join st_fund.t_st_gm_nzdhcpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_brinson_attribution_given_code(self, code):
        sql = "select jjdm, tjrq, portfolio_return, benchmark_return, asset_allo, sector_allo, equity_selection, trading, portfolio_weight, benchmark_weight from st_fund.r_st_hold_excess_attr_df where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_barra_attribution_given_code(self, code):
        sql = "select jjdm, tjrq, attr_type, style_factor, data_type, data_value from st_fund.r_st_nav_attr_df where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_gptzzjb_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, gptzzjb from st_fund.t_st_gm_zcpz where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_holding_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zqdm, zqmc, ccsz, ccsl, zjbl from st_fund.t_st_gm_gpzh where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_holding_diff_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zqdm, zqmc, zclb, zgblbd, sfsqzcg from st_fund.t_st_gm_jjcgbd where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_holding_semi_diff_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zqdm, zqmc, zzjbl, zjblpm, ggzjzbjbd from st_fund.t_st_gm_gpzhggtj where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_valuation_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zclb, pe, pb, roe, dividend from st_fund.t_st_gm_jjggfg where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=2000)
        return df

    def read_stock_valuation_given_date(self, date):
        sql = "select b.SECUCODE, to_char(a.TRADINGDAY, 'yyyyMMdd') as TRADINGDAY, a.TOTALMV, a.PE, a.PB from hsjy_gg.LC_DIndicesForValuation a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where to_char(a.TRADINGDAY, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly')
        return df

    def read_star_stock_valuation_given_date(self, date):
        sql = "select b.SECUCODE, to_char(a.TradingDay, 'yyyyMMdd') as TRADINGDAY, a.TotalMV as TOTALMV, a.PETTM as PE, a.PB from hsjy_gg.LC_STIBDIndiForValue a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where to_char(a.TradingDay, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly')
        return df

    # def read_stock_industry(self):
    #     sql = "select gsdm, xxfbrq, xxly, xyhfbz, ssxy, sfzx, qxrq, yjxydm, yjxymc, ejxydm, ejxymc from st_ashare.t_st_ag_gshyhfb"
    #     df = self.get_df(sql, db='alluser')
    #     return df

    def read_stock_industry(self):
        sql = "select zqdm, flmc, fldm, fljb, hyhfbz, qsrq, jsrq, sfyx, credt_etl from st_fund.t_st_gm_zqhyflb"
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_industry_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zclb, hyhfbz, fldm, flmc, zzjbl, hyzjzbjbd, hyzjzbltlpj, zgpbl, hyzgpbjbd, hyzgpbltlpj, zltgbl, hyzltgbjbd, hyzltgbltlpj from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_industry_theme(self):
        sql = "select hybh, hyzt, fldm, qsrq, jsrq from st_fund.t_st_gm_hyztpzb"
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_theme_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zblx, zclb, zgpszb, jsqbd, tlpj from st_fund.t_st_gm_ztcgbd where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_industry_info(self):
        sql = "select hyhfbz, fldm, flmc, zsdm, qsrq, jsrq, fljb, sfyx from st_market.t_st_zs_hyzsdmdyb"
        df = self.get_df(sql, db='alluser')
        return df

    def read_index_info(self):
        sql = "select a.IndexCode, b.SecuCode, b.ChiName, b.ChiNameAbbr from hsjy_gg.LC_IndexBasicInfo a left join hsjy_gg.SecuMain b on a.IndexCode=b.InnerCode"
        df = self.get_df(sql, db='readonly')
        return df

    def read_index_cons(self, index):
        sql = "select a.IndexCode, b.SecuCode, a.InfoSource, a.EndDate, a.Weight from hsjy_gg.LC_IndexComponentsWeight a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.IndexCode='{0}'".format(index)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_fund_style(self):
        sql = "select fund_id, trade_date, type, cap_score, vcg_score, category from st_fund.r_st_gm_equity_score"
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_stock_style(self):
        sql = "select ticker, trade_date, type, cap_score, vcg_score, category from st_fund.r_st_gp_equity_score"
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_barra_style_exposure_given_dates(self, dates):
        dates = '"' + '","'.join(dates) + '"'
        sql = "select ticker, trade_date, size, beta, momentum, resvol, btop, sizenl, liquidity, earnyield, growth, leverage from st_ashare.r_st_barra_style_factor where trade_date in ({0})".format(dates)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_index_daily_k_given_date_and_indexs(self, date, indexs):
        indexs = '"' + '","'.join(indexs) + '"'
        sql = "select scdm, zqdm, zqmc, jyrq, qspj, kpjg, spjg, zgjg, zdjg, zdsl, zdfd, bdfd, cjsl, cjjs, cjbs, ltsz, zsz from st_market.t_st_zs_hqql where jyrq>='{0}' and zqdm in ({1}) ".format(date, indexs)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_index_valuation_given_date_and_indexs(self, date, indexs):
        indexs = '"' + '","'.join(indexs) + '"'
        sql = "select scdm, zqdm, zqmc, jyrq, pe, pb, roe, gxl from st_market.t_st_zs_hqql where jyrq>='{0}' and zqdm in ({1}) ".format(date, indexs)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_fund_nav_given_date_and_codes(self, date, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, jjjz, ljjz from st_fund.t_st_gm_jjjz where jzrq>='{0}' and jjdm in ({1}) ".format(date, codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_nav_adj_given_date_and_codes(self, date, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, fqdwjz, hbfh, hbcl, hbdr from st_fund.t_st_gm_rhb where jzrq>='{0}' and jjdm in ({1}) ".format(date, codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_finance_data_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, ROETTM AS ROE_TTM, ROATTM AS ROA_TTM, ROICTTM AS ROIC_TTM, NetProfitRatioTTM AS NET_PROFIT_RATIO_TTM, GrossIncomeRatioTTM AS GROSS_INCOME_RATIO_TTM, EBITToToAssetsTTM AS EBIT_ASSET_RATIO_TTM from hsjy_gg.LC_MainIndexNew a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_market_value_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.NegotiableMV AS NEG_MARKET_VALUE from hsjy_gg.LC_DIndicesForValuation a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where to_char(a.TradingDay, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_bond_fund_info(self):
        sql = "select jjdm, jjmc, jjjc, clrq, zzrq, ejfl, kffb from st_fund.t_st_gm_jjxx where ejfl in ('22', '23', '24', '27')"
        df = self.get_df(sql, db='funduser')
        return df

    def read_bond_fund_position_given_code(self, code):
        sql = "select jjdm, jsrq, gptzsz, kzzsz from st_fund.t_st_gm_zcpz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_cumret_given_code(self, code, start, end):
        sql = "SELECT jjdm, jzrq, hbcl FROM funddb.jjhb WHERE jjdm = '{0}' AND jzrq >= {1} AND jzrq <= {2}".format(code, start, end)
        df = self.get_df(sql, db='readonly')
        return df


if __name__ == '__main__':
    dates = HBDB().read_fund_barra_attribution_given_code('450004')
    barra_style_exposure = HBDB().read_barra_style_exposure_given_dates(fund_zc_wmv['RECENT_TRADE_DATE'].unique().tolist())
    barra_style_exposure.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/barra_style_exposure.hdf', key='table', mode='w')