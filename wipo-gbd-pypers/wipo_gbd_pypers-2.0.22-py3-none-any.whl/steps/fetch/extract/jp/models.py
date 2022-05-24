import math
import yaml

# Basic Master  // Common stuff
tm_basic_info = "upd_t_basic_item_art.tsv"
tm_additional_info = "upd_t_add_info.tsv"
tm_txt_display = "upd_indct_use_t_art.tsv"
tm_txt_std_char = "upd_standard_char_t_art.tsv"
tm_txt_search = "upd_search_use_t_art_table.tsv"
tm_txt_transliteration = "upd_t_dsgnt_art.tsv"
tm_vienna = "upd_t_vienna_class_grphc_term_art.tsv"

# Application Master
tm_am_master = "upd_jiken_c_t.tsv"
tm_am_goods = "upd_jiken_c_t_shohin_joho.tsv"
tm_am_reps = "upd_jiken_c_t_shutugannindairinin.tsv"
tm_am_prio = "upd_jiken_c_t_yusenken_joho.tsv"

# Registration master
tm_rm_master = "upd_mgt_info_t.tsv"
tm_rm_goods = "upd_right_goods_name.tsv"
tm_rm_holders = "upd_right_person_art_t.tsv"
tm_rm_reps = "upd_atty_art_t.tsv"
tm_rm_first_use = "upd_t_first_indct_div.tsv.tsv"
tm_rm_prio = ""

tm_images = "upd_t_sample.tsv"

used_files = [
    tm_basic_info, tm_txt_transliteration, tm_txt_display, tm_txt_std_char, tm_txt_search, tm_vienna,
    tm_am_master, tm_am_reps, tm_am_goods, tm_am_prio,
    tm_rm_master, tm_rm_holders, tm_rm_reps, tm_rm_first_use, tm_rm_goods,
    tm_images
]


def first(series):
    if isinstance(series, str) or isinstance(series, int) or isinstance(series, float):
        return series
    if series.empty:
        return None
    if len(series.to_list()) > 0:
        return series.to_list()[0]
    return None


class BaseModel:
    _keys = []
    defaults = {
        "split_num": float('nan')
    }

    def keys(self):
        return self._keys

    def get_query(self, num, div):
        raise NotImplemented()

    def to_dict(self):
        tmp = {}
        for key in self._keys:
            tmp[key] = getattr(self, key)
        return {'tm': tmp}


class BasicApplicationTM(BaseModel):
    _keys = []
    defaults = {
        "split_num": float('nan')
    }

    def get_query(self, num, div):
        if isinstance(div, float) and math.isnan(div):
            return "%s == %s " % ("app_num", num)
        else:
            return "%s == %s and %s == '%s'" % ("app_num", num, "split_num", div)

    def __init__(self, num, div, tables):
        query_basic_master = self.get_query(num, div)
        self.num = num

        ## Basic Master (JPWT)
        self.base = tables[tm_basic_info].query(query_basic_master)
        self._keys.append("base")
        reg_num = first(self.base.reg_num)
        self.div = div
        self.key_str = str(num)
        if isinstance(div, float) and not math.isnan(div) and div != 0 and not div == BasicApplicationTM.defaults[
            "split_num"]:
            self.key_str += "/" + str(div)

        if tm_additional_info in tables:
            self.extra = tables[tm_additional_info].query(query_basic_master)
            self._keys.append("extra")

        if tm_vienna in tables:
            self.vienna = tables[tm_vienna].query(query_basic_master)
            self._keys.append("vienna")

        if tm_txt_display in tables:
            self.txt_display = tables[tm_txt_display].query(query_basic_master)
            self._keys.append("txt_display")

        if tm_txt_transliteration in tables:
            self.txt_transliteration = tables[tm_txt_transliteration].query(query_basic_master)
            self._keys.append("txt_transliteration")

        if tm_txt_search in tables:
            self.txt_search = tables[tm_txt_search].query(query_basic_master)
            self._keys.append("txt_search")
        if tm_txt_std_char in tables:
            self.txt_std_char = tables[tm_txt_std_char].query(query_basic_master)
            self._keys.append("txt_std_char")


class ApplicationMasterTM(BaseModel):

    def get_query(self, num, div):
        if isinstance(div, float) and math.isnan(div) or not div:
            return "%s == %s " % ("shutugan_no", num)
        else:
            return "%s == %s and %s == '%s'" % ("shutugan_no", num, "split_num", div)

    def __init__(self, num, div, tables):
        self.query_shutugan = self.get_query(num, div)
        self.master = tables[tm_am_master].query(self.query_shutugan)
        self.num = num

        # GOODS
        self.goods = []
        if tm_am_goods in tables:
            self.goods = tables[tm_am_goods].query(self.query_shutugan)
            self._keys.append("goods")

        # HOLDERS
        self.holders = []

        # REPRESENTATIVE
        self.reps = []
        if tm_am_reps in tables:
            tmp_reps = tables[tm_am_reps].query(self.query_shutugan)
            if tmp_reps.size > 0:
                self.reps = tmp_reps
            self._keys.append("reps")

        # PRIORITY
        self.prio = []
        if tm_am_prio in tables:
            tmp_prio = tables[tm_am_prio].query(self.query_shutugan)
            if tmp_prio.size > 0:
                self.prio = tmp_prio
            self._keys.append("prio")


class RegistrationMasterTM(BaseModel):

    def get_query(self, num, div):
        query_reg_num = "%s == %s and %s == %s" % ("reg_num", num, "split_num", div)
        return query_reg_num

    def __init__(self, num, div, tables):
        self.query_reg_num = self.get_query(num, div)
        self.master = tables[tm_rm_master].query(self.query_reg_num)
        self.num = num
        # GOODS
        self.goods = []
        if tm_rm_goods in tables:
            self.goods = tables[tm_rm_goods].query(self.query_reg_num)
            self._keys.append("goods")

        # HOLDERS
        self.holders = []
        if tm_rm_holders in tables:
            tmp_holders = tables[tm_rm_holders].query(self.query_reg_num)
            # self.merge_holders(tmp_holders)
            if tmp_holders.size > 0:
                self.holders = tmp_holders
            self._keys.append("holders")

        # REPRESENTATIVE
        self.reps = []
        if tm_rm_reps in tables:
            tmp_reps = tables[tm_rm_reps].query(self.query_reg_num)
            if tmp_reps.size > 0:
                # self.merge_reps(tmp_reps)
                self.reps = tmp_reps

            self._keys.append("reps")

        # WO REFERENCE
        self.refs = []
        if tm_rm_first_use in tables:
            tmp_refs = tables[tm_rm_first_use].query(self.query_reg_num)
            if tmp_refs.size > 0:
                # self.merge_reps(tmp_reps)
                self.refs = tmp_refs

            self._keys.append("refs")

        # PRIORITY so far in the main table, but only date and country
        self.prio = []
        if tm_rm_prio in tables:
            tmp_prio = tables[tm_rm_prio].query(self.query_reg_num)
            if tmp_prio.size > 0:
                self.prio = tmp_prio
            self._keys.append("prio")
