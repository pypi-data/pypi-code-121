from copy import (
    deepcopy,
)
from enum import (
    Enum,
)
from functools import (
    lru_cache,
)
from itertools import (
    chain,
    combinations,
)
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

from botoolkit.core.helpers import (
    topological_sort,
)


class ProjectEnum(Enum):
    """
    Перечисление проектов web_bb
    """

    WEB_BB_APP = 'web_bb_app'
    WEB_BB_CORE = 'web_bb_core'
    WEB_BB_ACCOUNTING = 'web_bb_accounting'
    WEB_BB_SALARY = 'web_bb_salary'
    WEB_BB_FOOD = 'web_bb_food'
    WEB_BB_VEHICLE = 'web_bb_vehicle'
    WEB_BB_BEHAVE = 'web_bb_behave'

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def get_dependencies(cls) -> Dict['ProjectEnum', Tuple['ProjectEnum']]:
        dependencies = {
            cls.WEB_BB_VEHICLE: (
                cls.WEB_BB_ACCOUNTING,
            ),
            cls.WEB_BB_FOOD: (
                cls.WEB_BB_ACCOUNTING,
            ),
        }

        return dependencies

    @classmethod
    @lru_cache()
    def get_projects(cls):
        """
        Возвращает кортеж проектов
        """
        return (
            ProjectEnum.WEB_BB_ACCOUNTING,
            ProjectEnum.WEB_BB_SALARY,
            ProjectEnum.WEB_BB_FOOD,
            ProjectEnum.WEB_BB_VEHICLE,
        )

    @classmethod
    @lru_cache()
    def get_projects_combinations(
        cls,
        projects: Tuple['ProjectEnum'] = None,
    ) -> List[Tuple['ProjectEnum']]:
        """
        Возвращает допустимые комбинации проектов
        """
        projects = (
            sorted(filter(None, projects)) if
            projects else
            sorted(cls.get_projects())
        )

        dirty_combinations = list(
            chain(*list(combinations(projects, index) for index in range(1, 5)))
        )

        filtered_combinations = []

        project_dependencies = ProjectEnum.get_dependencies()

        for dirty_combination in dirty_combinations:
            is_dirty = False

            for dependent_project in project_dependencies:
                if (
                    dependent_project in dirty_combination and
                    not all(
                        main_project in dirty_combination
                        for main_project in
                        project_dependencies[dependent_project]
                    )
                ):
                    is_dirty = True

            if not is_dirty:
                filtered_combinations.append(dirty_combination)

        return filtered_combinations

    @classmethod
    @lru_cache()
    def get_projects_weights(cls):
        """
        Возвращает веса проектов относительно времени выполнения раскатки
        миграций
        """
        return {
            cls.WEB_BB_SALARY: 4,
            cls.WEB_BB_ACCOUNTING: 3,
            cls.WEB_BB_FOOD: 2,
            cls.WEB_BB_VEHICLE: 1
        }

    @classmethod
    @lru_cache()
    def get_projects_combination_weight(
        cls,
        projects_combination: Tuple['ProjectEnum'],
    ):
        """
        Возвращает вес комбинации проектов согласно времени раскатки миграций
        """
        projects_weights = cls.get_projects_weights()

        return sum(
            projects_weights[project]
            for project in projects_combination
        )

    def short(self):
        """
        Возвращает сокращенное название проекта
        """
        return self.value.replace('web_bb_', '')


class ProjectPluginEnum(Enum):
    """
    Перечисление плагинов проектов
    """

    # Общие плагины
    WEB_BB = 'web_bb'
    WEB_BB_MIS_INTEGRATION_SERVICE = 'web_bb.mis_integration_service'
    WEB_BB_SVODY = 'web_bb.svody'
    WEB_BB_WEBSERVICES = 'web_bb.webservices'
    WEBSERVICES = 'webservices'

    # Плагины Бухгалтерии
    ACCOUNTING = 'accounting'
    ACCOUNTING_EDM = 'accounting_edm'
    ACCOUNTING_EDM_NSO = 'accounting_edm_nso'
    ACCOUNTING_EDM_RT = 'accounting_edm_rt'
    ACCOUNTING_MIS_INTEGRATION_SERVICE = 'accounting_mis_integration_service'
    ACCOUNTING_WEBSERVICES = 'accounting_webservices'
    ACCOUNT_STATEMENT = 'account_statement'
    ACK = 'ack'
    ANALYTIC_KVD_CARDS = 'analytic_kvd_cards'
    BS_EXCHANGE = 'bs_exchange'
    BUDGET_ASSIGNMENTS = 'budget_assignments'
    BUDGET_NOTICE = 'budget_notice'
    BUDGET_SMART = 'budget_smart'
    CONTRACT_PROCUREMENT_FOR_NODE = 'contract_procurement_for_node'
    CONTRACT_SUBJECT_FROM_INC_INVOICE = 'contract_subject_from_inc_invoice'
    CS_INTEGRATION = 'cs_integration'
    DEMO = 'demo'
    DORABOTKA_KOV = 'dorabotka_kov'
    DORABOTKA_KOV_SARATOV = 'dorabotka_kov_saratov'
    EXPORT_CLIENT_BANK = 'export_client_bank'
    EXPORT_CLIENT_BANK_SAMARA = 'export_client_bank_samara'
    IMPORT_ACK = 'import_ack'
    IMPORT_ADB = 'import_adb'
    IMPORT_BUAU = 'import_buau'
    IMPORT_FROM_AIST = 'import_from_aist'
    IMPORT_INVOICE = 'import_invoice'
    IMPORT_MOL = 'import_mol'
    IMPORT_PP = 'import_pp'
    IMPORT_PP_BFT = 'import_pp_bft'
    IMPORT_PP_CHELYAB_BUAU = 'import_pp_chelyab_buau'
    IMPORT_PP_NOVOSIB = 'import_pp_novosib'
    IMPORT_PP_SAMARA = 'import_pp_samara'
    IMPORT_PP_SUFD = 'import_pp_sufd'
    IMPORT_PP_TXT = 'import_pp_txt'
    IMPORT_SUFD_FO = 'import_sufd_fo'
    INTEGRATION_ACK = 'integration_ack'
    INTEGRATION_EIS = 'integration_eis'
    INTEGRATION_EL_BUDG = 'integration_el_budg'
    JOURNAL_HOZ_OPER_CHELYAB = 'journal_hoz_oper_chelyab'
    KAZAN_REPORTS = 'kazan_reports'
    KPP_PP = 'kpp_pp'
    KV_CHELYAB = 'kv_chelyab'
    LOAD_LIMITS = 'load_limits'
    LOAD_PLAN = 'load_plan'
    MAGIC_ANALYTIC = 'magic_analytic'
    MCHS = 'mchs'
    NOMER_DOGOVORA = 'nomer_dogovora'
    NOVOSIB_SERVICE_PF_ACT = 'novosib_service_pf_act'
    OPERATIONS_JOURNAL_04_ACCOUNTS_ANALYTICS = 'operations_journal_04_accounts_analytics'
    OSS = 'oss'
    PAYMENT_SCHEDULE = 'payment_schedule'
    PREDMET_DOGOVORA_0503769A = 'predmet_dogovora_0503769a'
    PROPERTY_INTEGRATION = 'property_integration'
    REESTR_IZVESHCHENIY = 'reestr_izveshcheniy'
    REESTR_IZVESHCHENIY_EIS = 'reestr_izveshcheniy_eis'
    RISGMP = 'risgmp'
    SOSTOYANIE_DOGOVOR = 'sostoyanie_dogovor'
    SUPPLY_CONTROL = 'supply_control'
    SUPPLIER_PERSONALITIES = 'supplier_personalities'
    TAXNET_INTEGRATION = 'taxnet_integration'
    UDMURTIA_UFK = 'udmurtia_ufk'
    URM_KRISTA = 'urm_krista'

    # Плигины ЗиК
    SALARY = 'salary'
    SALARY_ACCOUNTING_INTEGRATION = 'salary.accounting_integration'
    SALARY_CHELYAB_ZDRAV = 'salary.chelyab_zdrav'
    SALARY_CIVIL_SERVICE = 'salary.civil_service'
    SALARY_DIGITAL_PAYSLIP = 'salary.digital_payslip'
    SALARY_DOCUMENT_FLOW_DOCUMENT_REGISTER = 'salary.document_flow.document_register'
    SALARY_EDUCATION = 'salary.education'
    SALARY_EDUCATION_PLANNING = 'salary.education_planning'
    SALARY_EFFECTIVE_CONTRACT = 'salary.effective_contract'
    SALARY_EGISZ = 'salary.egisz'
    SALARY_EHDO = 'salary.ehdo'
    SALARY_EISKS = 'salary.eisks'
    SALARY_EISU_KS = 'salary.eisu_ks'
    SALARY_ELN = 'salary.eln'
    SALARY_EMPLOYEE_ATTESTATION = 'salary.employee_attestation'
    SALARY_EXTRA_ALGORITHMS = 'salary.extra_algorithms'
    SALARY_FK = 'salary.fk'
    SALARY_FSS_ENCRYPTION = 'salary.fss_encryption'
    SALARY_GMS_INFORMATION = 'salary.gms_information'
    SALARY_JINN_SERVICE = 'salary.jinn_service'
    SALARY_LDAP_SYNC = 'salary.ldap_sync'
    SALARY_NOVOSIB_ZDRAV = 'salary.novosib_zdrav'
    SALARY_PERSONNEL_RESERVE_PLUGIN = 'salary.personnel_reserve_plugin'
    SALARY_PORTAL_INTEGRATION = 'salary.portal_integration'
    SALARY_REGIONAL_PLUGINS_IVANOVO = 'salary.regional_plugins.ivanovo'
    SALARY_REGIONAL_PLUGINS_KALININGRAD = 'salary.regional_plugins.kaliningrad'
    SALARY_REGIONAL_PLUGINS_KAZAN = 'salary.regional_plugins.kazan'
    SALARY_REGIONAL_PLUGINS_RT = 'salary.regional_plugins.rt'
    SALARY_REGIONAL_PLUGINS_SAMARA = 'salary.regional_plugins.samara'
    SALARY_REGIONAL_PLUGINS_TATARSTAN = 'salary.regional_plugins.tatarstan'
    SALARY_REGIONAL_PLUGINS_TOMSK = 'salary.regional_plugins.tomsk'
    SALARY_ROSEL = 'salary.rosel'
    SALARY_ROSTRANSNADZOR = 'salary.rostransnadzor'
    SALARY_SERVICE = 'salary.service'
    SALARY_SLR_MIS = 'salary.slr_mis'
    SALARY_SLR_SVODY = 'salary.slr_svody'
    SALARY_SPORT = 'salary.sport'
    SALARY_STAFFING_STRENGTH_EXPORT = 'salary.staffing_strength_export'
    SALARY_WORK_SCHEDULE = 'salary.work_schedule'
    SALARY_ZDRAV = 'salary.zdrav'
    SALARY_SAMARA = 'salary_samara'
    SALARY_WEBSERVICES = 'salary_webservices'
    SLR_BANK_EXCHANGE = 'slr_bank_exchange'
    DESIGNATED_EMPLOYEES = 'designated_employees'
    SALARY_BARS_GROUP = 'salary.bars_group'

    # Плагины Авто
    VEHICLE = 'vehicle'
    VEHICLE_VEHICLE_CHELYAB_EXTEND = 'vehicle.vehicle_chelyab_extend'
    VEHICLE_VEHICLE_NOVOSIB_EXTEND = 'vehicle.vehicle_novosib_extend'
    SSMP_INTEGRATION = 'ssmp_integration'
    VEHICLE_SALARY_INTEGRATION = 'vehicle.salary_integration'

    # Плагины Питания
    FOOD = 'food'
    FOOD_FOOD_CHELYAB_EXTEND = 'food.food_chelyab_extend'
    FOOD_FOOD_MENU_DEMAND_EXTEND = 'food.food_menu_demand_extend'
    FOOD_FOOD_NOVOSIB_EXTEND = 'food.food_novosib_extend'
    FOOD_FOOD_SARATOV_EXTEND = 'food.food_saratov_extend'
    FOOD_MIS_INTEGRATION = 'food_mis_integration'

    # Плагины для тестирования
    WEB_BB_BEHAVE = 'web_bb_behave'
    BEHAVE_TEST_RECORDER = 'behave_test_recorder'
    ACCOUNTING_BEHAVE_TEST_RECORDER = 'accounting_behave_test_recorder'
    SALARY_BEHAVE_TEST_RECORDER = 'salary_behave_test_recorder'

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def get_all_plugins(cls):
        """
        Возвращает множество всех плагинов
        """
        all_plugins = set(
            chain(
                *list(
                    [
                        cls.get_general_plugins(),
                        cls.get_accounting_plugins(),
                        cls.get_food_plugins(),
                        cls.get_salary_plugins(),
                        cls.get_vehicle_plugins(),
                        cls.get_behave_plugins(),
                    ]
                )
            )
        )

        return all_plugins

    @classmethod
    def get_all_plugins_str(cls):
        """
        Возвращает все плагины в строковом представлении
        """
        all_plugins = cls.get_all_plugins()

        return set(
            map(lambda plugin: plugin.value, all_plugins)
        )

    @classmethod
    def get_general_plugins(
        cls,
        only_base: bool = False,
    ) -> List['ProjectPluginEnum']:
        """
        Возвращает список общих плагинов
        """
        plugins = [
            cls.WEB_BB,
        ]

        if not only_base:
            plugins.extend(
                (
                    cls.WEB_BB_MIS_INTEGRATION_SERVICE,
                    cls.WEB_BB_SVODY,
                    cls.WEB_BB_WEBSERVICES,
                    cls.WEBSERVICES,
                )
            )

        return plugins

    @classmethod
    def get_general_dependencies(cls) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum']]:
        """
        Возвращает словарь зависимостей общих плагинов
        """
        return {
            cls.WEB_BB: (),
            cls.WEB_BB_MIS_INTEGRATION_SERVICE: (
                cls.WEB_BB,
            ),
            cls.WEB_BB_SVODY: (
                cls.WEB_BB,
            ),
            cls.WEB_BB_WEBSERVICES: (
                cls.WEB_BB,
            ),
            cls.WEBSERVICES: (
                cls.WEB_BB,
            ),
        }

    @classmethod
    def get_accounting_plugins(
        cls,
        only_base: bool = False,
    ) -> List['ProjectPluginEnum']:
        """
        Возвращает список плагинов Бухгалтерии
        """
        plugins = [
            cls.ACCOUNTING,
        ]

        if not only_base:
            plugins.extend(
                (
                    cls.ACCOUNTING_EDM,
                    cls.ACCOUNTING_EDM_NSO,
                    cls.ACCOUNTING_EDM_RT,
                    cls.ACCOUNTING_MIS_INTEGRATION_SERVICE,
                    cls.ACCOUNTING_WEBSERVICES,
                    cls.ACCOUNT_STATEMENT,
                    cls.ACK,
                    cls.ANALYTIC_KVD_CARDS,
                    cls.BS_EXCHANGE,
                    cls.BUDGET_ASSIGNMENTS,
                    cls.BUDGET_NOTICE,
                    cls.BUDGET_SMART,
                    cls.CONTRACT_PROCUREMENT_FOR_NODE,
                    cls.CONTRACT_SUBJECT_FROM_INC_INVOICE,
                    cls.CS_INTEGRATION,
                    cls.DEMO,
                    cls.DORABOTKA_KOV,
                    cls.DORABOTKA_KOV_SARATOV,
                    cls.EXPORT_CLIENT_BANK,
                    cls.EXPORT_CLIENT_BANK_SAMARA,
                    cls.IMPORT_ACK,
                    cls.IMPORT_ADB,
                    cls.IMPORT_BUAU,
                    cls.IMPORT_FROM_AIST,
                    cls.IMPORT_INVOICE,
                    cls.IMPORT_MOL,
                    cls.IMPORT_PP,
                    cls.IMPORT_PP_BFT,
                    cls.IMPORT_PP_CHELYAB_BUAU,
                    cls.IMPORT_PP_NOVOSIB,
                    cls.IMPORT_PP_SAMARA,
                    cls.IMPORT_PP_SUFD,
                    cls.IMPORT_PP_TXT,
                    cls.IMPORT_SUFD_FO,
                    cls.INTEGRATION_ACK,
                    cls.INTEGRATION_EIS,
                    cls.INTEGRATION_EL_BUDG,
                    cls.JOURNAL_HOZ_OPER_CHELYAB,
                    cls.KAZAN_REPORTS,
                    cls.KPP_PP,
                    cls.KV_CHELYAB,
                    cls.LOAD_LIMITS,
                    cls.LOAD_PLAN,
                    cls.MAGIC_ANALYTIC,
                    cls.MCHS,
                    cls.NOMER_DOGOVORA,
                    cls.NOVOSIB_SERVICE_PF_ACT,
                    cls.OSS,
                    cls.PAYMENT_SCHEDULE,
                    cls.PROPERTY_INTEGRATION,
                    cls.REESTR_IZVESHCHENIY,
                    cls.REESTR_IZVESHCHENIY_EIS,
                    cls.RISGMP,
                    cls.SOSTOYANIE_DOGOVOR,
                    cls.TAXNET_INTEGRATION,
                    cls.URM_KRISTA,
                    cls.PREDMET_DOGOVORA_0503769A,
                    cls.SUPPLY_CONTROL,
                    cls.SUPPLIER_PERSONALITIES,
                    cls.OPERATIONS_JOURNAL_04_ACCOUNTS_ANALYTICS,
                    cls.UDMURTIA_UFK,
                )
            )

        return plugins

    @classmethod
    def get_accounting_dependencies(cls) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum']]:
        """
        Возвращает словарь зависимостей плагинов Бухгалтерии
        """
        return {
            cls.ACCOUNTING: (
                cls.WEB_BB,
                cls.WEB_BB_SVODY,
            ),
            cls.ACCOUNTING_EDM: (
                cls.ACCOUNTING,
            ),
            cls.ACCOUNTING_EDM_NSO: (
                cls.ACCOUNTING_EDM,
            ),
            cls.ACCOUNTING_EDM_RT: (
                cls.ACCOUNTING_EDM,
            ),
            cls.ACCOUNTING_MIS_INTEGRATION_SERVICE: (
                cls.ACCOUNTING,
            ),
            cls.ACCOUNTING_WEBSERVICES: (
                cls.ACCOUNTING,
                cls.WEB_BB_WEBSERVICES,
            ),
            cls.ACCOUNT_STATEMENT: (
                cls.ACCOUNTING,
            ),
            cls.ACK: (
                cls.KPP_PP,
            ),
            cls.ANALYTIC_KVD_CARDS: (
                cls.ACCOUNTING,
            ),
            cls.BS_EXCHANGE: (
                cls.ACCOUNTING,
            ),
            cls.BUDGET_ASSIGNMENTS: (
                cls.ACCOUNTING,
            ),
            cls.BUDGET_NOTICE: (
                cls.ACCOUNTING,
            ),
            cls.BUDGET_SMART: (
                cls.ACCOUNTING,
            ),
            cls.CONTRACT_PROCUREMENT_FOR_NODE: (
                cls.ACCOUNTING,
            ),
            cls.CONTRACT_SUBJECT_FROM_INC_INVOICE: (
                cls.ACCOUNTING,
            ),
            cls.CS_INTEGRATION: (
                cls.ACCOUNTING,
            ),
            cls.DEMO: (
                cls.ACCOUNTING,
            ),
            cls.DORABOTKA_KOV: (
                cls.ACCOUNTING,
            ),
            cls.DORABOTKA_KOV_SARATOV: (
                cls.ACCOUNTING,
            ),
            cls.EXPORT_CLIENT_BANK: (
                cls.ACCOUNTING,
            ),
            cls.EXPORT_CLIENT_BANK_SAMARA: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_ACK: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_ADB: (
                cls.ACCOUNT_STATEMENT,
            ),
            cls.IMPORT_BUAU: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_FROM_AIST: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_INVOICE: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_MOL: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_PP: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_PP_BFT: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_PP_CHELYAB_BUAU: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_PP_NOVOSIB: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_PP_SAMARA: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_PP_SUFD: (
                cls.ACCOUNT_STATEMENT,
            ),
            cls.IMPORT_PP_TXT: (
                cls.ACCOUNTING,
            ),
            cls.IMPORT_SUFD_FO: (
                cls.ACCOUNTING,
            ),
            cls.INTEGRATION_ACK: (
                cls.ACCOUNT_STATEMENT,
            ),
            cls.INTEGRATION_EIS: (
                cls.ACCOUNTING,
            ),
            cls.INTEGRATION_EL_BUDG: (
                cls.ACCOUNTING,
            ),
            cls.JOURNAL_HOZ_OPER_CHELYAB: (
                cls.ACCOUNTING,
            ),
            cls.KAZAN_REPORTS: (
                cls.ACCOUNTING,
            ),
            cls.KPP_PP: (
                cls.ACCOUNTING,
            ),
            cls.KV_CHELYAB: (
                cls.ACCOUNTING,
            ),
            cls.LOAD_LIMITS: (
                cls.ACCOUNTING,
            ),
            cls.LOAD_PLAN: (
                cls.ACCOUNTING,
            ),
            cls.MAGIC_ANALYTIC: (
                cls.ACCOUNTING,
            ),
            cls.MCHS: (
                cls.ACCOUNTING,
            ),
            cls.NOMER_DOGOVORA: (
                cls.ACCOUNTING,
            ),
            cls.NOVOSIB_SERVICE_PF_ACT: (
                cls.ACCOUNTING,
            ),
            cls.OSS: (
                cls.ACCOUNTING,
            ),
            cls.PAYMENT_SCHEDULE: (
                cls.ACCOUNTING,
            ),
            cls.PROPERTY_INTEGRATION: (
                cls.ACCOUNTING,
            ),
            cls.REESTR_IZVESHCHENIY: (
                cls.ACCOUNTING,
            ),
            cls.REESTR_IZVESHCHENIY_EIS: (
                cls.ACCOUNTING,
            ),
            cls.RISGMP: (
                cls.ACCOUNTING,
            ),
            cls.SOSTOYANIE_DOGOVOR: (
                cls.ACCOUNTING,
            ),
            cls.TAXNET_INTEGRATION: (
                cls.ACCOUNTING,
            ),
            cls.URM_KRISTA: (
                cls.ACCOUNTING,
            ),
            cls.PREDMET_DOGOVORA_0503769A: (
                cls.ACCOUNTING,
            ),
            cls.SUPPLY_CONTROL: (
                cls.ACCOUNTING,
            ),
            cls.SUPPLIER_PERSONALITIES: (
                cls.ACCOUNTING,
            ),
            cls.OPERATIONS_JOURNAL_04_ACCOUNTS_ANALYTICS: (
                cls.ACCOUNTING,
            ),
            cls.UDMURTIA_UFK: (
                cls.ACCOUNTING,
            ),
        }

    @classmethod
    def get_salary_plugins(
        cls,
        only_base: bool = False,
    ) -> List['ProjectPluginEnum']:
        """
        Возвращает список плагинов ЗиК
        """
        plugins = [
            cls.SALARY,
        ]

        if not only_base:
            plugins.extend(
                (
                    cls.SALARY_ACCOUNTING_INTEGRATION,
                    cls.SALARY_CHELYAB_ZDRAV,
                    cls.SALARY_CIVIL_SERVICE,
                    cls.SALARY_DIGITAL_PAYSLIP,
                    cls.SALARY_DOCUMENT_FLOW_DOCUMENT_REGISTER,
                    cls.SALARY_EDUCATION,
                    cls.SALARY_EDUCATION_PLANNING,
                    cls.SALARY_EFFECTIVE_CONTRACT,
                    cls.SALARY_EGISZ,
                    cls.SALARY_EHDO,
                    cls.SALARY_EISU_KS,
                    cls.SALARY_EISKS,
                    cls.SALARY_ELN,
                    cls.SALARY_EMPLOYEE_ATTESTATION,
                    cls.SALARY_EXTRA_ALGORITHMS,
                    cls.SALARY_FK,
                    cls.SALARY_FSS_ENCRYPTION,
                    cls.SALARY_GMS_INFORMATION,
                    cls.SALARY_JINN_SERVICE,
                    cls.SALARY_LDAP_SYNC,
                    cls.SALARY_NOVOSIB_ZDRAV,
                    cls.SALARY_PERSONNEL_RESERVE_PLUGIN,
                    cls.SALARY_PORTAL_INTEGRATION,
                    cls.SALARY_REGIONAL_PLUGINS_IVANOVO,
                    cls.SALARY_REGIONAL_PLUGINS_KALININGRAD,
                    cls.SALARY_REGIONAL_PLUGINS_KAZAN,
                    cls.SALARY_REGIONAL_PLUGINS_RT,
                    cls.SALARY_REGIONAL_PLUGINS_SAMARA,
                    cls.SALARY_REGIONAL_PLUGINS_TATARSTAN,
                    cls.SALARY_REGIONAL_PLUGINS_TOMSK,
                    cls.SALARY_ROSEL,
                    cls.SALARY_ROSTRANSNADZOR,
                    cls.SALARY_SERVICE,
                    cls.SALARY_SLR_MIS,
                    cls.SALARY_SLR_SVODY,
                    cls.SALARY_SPORT,
                    cls.SALARY_STAFFING_STRENGTH_EXPORT,
                    cls.SALARY_WORK_SCHEDULE,
                    cls.SALARY_ZDRAV,
                    cls.SALARY_SAMARA,
                    cls.SALARY_WEBSERVICES,
                    cls.SLR_BANK_EXCHANGE,
                    cls.DESIGNATED_EMPLOYEES,
                    cls.SALARY_BARS_GROUP,
                )
            )

        return plugins

    @classmethod
    def get_salary_dependencies(cls) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum']]:
        """
        Возвращает словарь зависимостей плагинов ЗиК
        """
        return {
            cls.SALARY: (
                cls.WEB_BB,
            ),
            # Временно убрана зависимость, т.к. в salary.novosib_zdrav.nsk_accounting_integration.models.OperationSetupAccNskExtra
            # есть ссылка на salary.accounting_integration.operation_setup.models.OperationSetupAcc.
            # Т.е. у salary.novosib_zdrav есть зависимость от salary.accounting_integration
            cls.SALARY_ACCOUNTING_INTEGRATION: (
                cls.SALARY,
            ),
            cls.SALARY_CHELYAB_ZDRAV: (
                cls.SALARY,
            ),
            cls.SALARY_CIVIL_SERVICE: (
                cls.SALARY,
            ),
            cls.SALARY_DIGITAL_PAYSLIP: (
                cls.SALARY,
            ),
            cls.SALARY_DOCUMENT_FLOW_DOCUMENT_REGISTER: (
                cls.SALARY,
            ),
            cls.SALARY_EDUCATION: (
                cls.SALARY,
            ),
            cls.SALARY_EDUCATION_PLANNING: (
                cls.SALARY,
            ),
            cls.SALARY_EFFECTIVE_CONTRACT: (
                cls.SALARY,
            ),
            cls.SALARY_EGISZ: (
                cls.SALARY,
            ),
            cls.SALARY_EHDO: (
                cls.SALARY,
            ),
            cls.SALARY_EISU_KS: (
                cls.SALARY,
            ),
            cls.SALARY_EISKS: (
                cls.SALARY,
            ),
            cls.SALARY_ELN: (
                cls.SALARY,
            ),
            cls.SALARY_EMPLOYEE_ATTESTATION: (
                cls.SALARY,
            ),
            cls.SALARY_EXTRA_ALGORITHMS: (
                cls.SALARY,
            ),
            cls.SALARY_FK: (
                cls.SALARY,
            ),
            cls.SALARY_FSS_ENCRYPTION: (
                cls.SALARY,
            ),
            cls.SALARY_GMS_INFORMATION: (
                cls.SALARY,
            ),
            cls.SALARY_JINN_SERVICE: (
                cls.SALARY,
            ),
            cls.SALARY_LDAP_SYNC: (
                cls.SALARY,
            ),
            cls.SALARY_NOVOSIB_ZDRAV: (
                cls.SALARY_ACCOUNTING_INTEGRATION,
            ),
            cls.SALARY_PERSONNEL_RESERVE_PLUGIN: (
                cls.SALARY,
            ),
            cls.SALARY_PORTAL_INTEGRATION: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_IVANOVO: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_KALININGRAD: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_KAZAN: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_RT: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_SAMARA: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_TATARSTAN: (
                cls.SALARY,
            ),
            cls.SALARY_REGIONAL_PLUGINS_TOMSK: (
                cls.SALARY,
            ),
            cls.SALARY_ROSEL: (
                cls.SALARY,
            ),
            cls.SALARY_ROSTRANSNADZOR: (
                cls.SALARY,
            ),
            cls.SALARY_SERVICE: (
                cls.SALARY,
            ),
            cls.SALARY_SLR_MIS: (
                cls.SALARY,
            ),
            cls.SALARY_SLR_SVODY: (
                cls.SALARY,
                cls.WEB_BB_SVODY,
            ),
            cls.SALARY_SPORT: (
                cls.SALARY,
            ),
            cls.SALARY_STAFFING_STRENGTH_EXPORT: (
                cls.SALARY,
            ),
            cls.SALARY_WORK_SCHEDULE: (
                cls.SALARY,
            ),
            cls.SALARY_ZDRAV: (
                cls.SALARY,
            ),
            cls.SALARY_SAMARA: (
                cls.SALARY,
            ),
            cls.SALARY_WEBSERVICES: (
                cls.SALARY,
            ),
            cls.SLR_BANK_EXCHANGE: (
                cls.SALARY,
            ),
            cls.DESIGNATED_EMPLOYEES: (
                cls.SALARY,
            ),
            cls.SALARY_BARS_GROUP: (
                cls.SALARY,
            ),
        }

    @classmethod
    def get_vehicle_plugins(
        cls,
        only_base: bool = False,
    ) -> List['ProjectPluginEnum']:
        """
        Возвращает список плагинов Авто
        """
        plugins = [
            cls.VEHICLE,
        ]

        if not only_base:
            plugins.extend(
                (
                    cls.VEHICLE_VEHICLE_CHELYAB_EXTEND,
                    cls.VEHICLE_VEHICLE_NOVOSIB_EXTEND,
                    cls.SSMP_INTEGRATION,
                    cls.VEHICLE_SALARY_INTEGRATION,
                )
            )

        return plugins

    @classmethod
    def get_vehicle_dependencies(cls) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum']]:
        """
        Возвращает словарь зависимостей плагинов Авто
        """
        return {
            cls.VEHICLE: (
                cls.ACCOUNTING,
            ),
            cls.VEHICLE_VEHICLE_CHELYAB_EXTEND: (
                cls.VEHICLE,
            ),
            cls.VEHICLE_VEHICLE_NOVOSIB_EXTEND: (
                cls.VEHICLE,
            ),
            cls.SSMP_INTEGRATION: (
                cls.VEHICLE,
            ),
            cls.VEHICLE_SALARY_INTEGRATION: (
                cls.VEHICLE,
                cls.SALARY,
            ),
        }

    @classmethod
    def get_food_plugins(
        cls,
        only_base: bool = False,
    ) -> List['ProjectPluginEnum']:
        """
        Возвращает список плагинов Питания
        """
        plugins = [
            cls.FOOD,
        ]

        if not only_base:
            plugins.extend(
                (
                    cls.FOOD_FOOD_CHELYAB_EXTEND,
                    cls.FOOD_FOOD_MENU_DEMAND_EXTEND,
                    cls.FOOD_FOOD_NOVOSIB_EXTEND,
                    cls.FOOD_FOOD_SARATOV_EXTEND,
                    cls.FOOD_MIS_INTEGRATION,
                )
            )

        return plugins

    @classmethod
    def get_food_dependencies(cls) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum']]:
        """
        Возвращает словарь зависимостей плагинов Питание
        """
        return {
            cls.FOOD: (
                cls.ACCOUNTING,
            ),
            cls.FOOD_FOOD_CHELYAB_EXTEND: (
                cls.FOOD,
            ),
            cls.FOOD_FOOD_MENU_DEMAND_EXTEND: (
                cls.FOOD,
            ),
            cls.FOOD_FOOD_NOVOSIB_EXTEND: (
                cls.FOOD,
            ),
            cls.FOOD_FOOD_SARATOV_EXTEND: (
                cls.FOOD,
            ),
            cls.FOOD_MIS_INTEGRATION: (
                cls.FOOD,
            ),
        }

    @classmethod
    def get_behave_plugins(
        cls,
        only_base: bool = False
    ):
        """
        Возвращает список плагинов для тестов
        """
        plugins = [
            cls.WEB_BB_BEHAVE,
        ]

        if not only_base:
            plugins.extend(
                (
                    cls.BEHAVE_TEST_RECORDER,
                    cls.ACCOUNTING_BEHAVE_TEST_RECORDER,
                    cls.SALARY_BEHAVE_TEST_RECORDER,
                )
            )

        return plugins

    @classmethod
    def get_behave_dependencies(cls) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum']]:
        """
        Возвращает словарь зависимостей плагинов Тестирования
        """
        return {
            cls.WEB_BB_BEHAVE: (
                cls.WEB_BB,
            ),
            cls.BEHAVE_TEST_RECORDER: (
                cls.WEB_BB_BEHAVE,
            ),
            cls.ACCOUNTING_BEHAVE_TEST_RECORDER: (
                cls.BEHAVE_TEST_RECORDER,
                cls.ACCOUNTING,
            ),
            cls.SALARY_BEHAVE_TEST_RECORDER: (
                cls.BEHAVE_TEST_RECORDER,
                cls.SALARY,
            ),
        }

    @classmethod
    def get_plugins_dependencies(
        cls,
    ) -> Dict['ProjectPluginEnum', Tuple['ProjectPluginEnum', ...]]:
        """
        Возвращает словарь зависимостей между плагинами
        """
        return {
            **cls.get_general_dependencies(),
            **cls.get_accounting_dependencies(),
            **cls.get_salary_dependencies(),
            **cls.get_vehicle_dependencies(),
            **cls.get_food_dependencies(),
            **cls.get_behave_dependencies(),
        }

    @classmethod
    def sort_plugins_by_dependencies(cls, plugins: List['ProjectPluginEnum']):
        """
        Сортировка списка плагинов по уровню зависимости между ними
        """
        all_dependencies = cls.get_plugins_dependencies()
        dependency_pairs = []

        for plugin in plugins:
            if plugin in all_dependencies:
                for required_plugin in all_dependencies[plugin]:
                    dependency_pairs.append((plugin.value, required_plugin.value))
            else:
                raise RuntimeError(f'Плагин {plugin} отсутствует в зарегистрированных зависимостях плагинов')

        sorted_result = topological_sort(
            dependency_pairs=dependency_pairs,
        )

        sorted_result_plugins = (
            list(reversed(sorted_result.sorted)) + sorted_result.cyclic
        )
        without_dependencies = set(plugin.value for plugin in plugins).difference(sorted_result_plugins)
        sorted_tool_plugins = list(without_dependencies) + sorted_result_plugins

        return [cls(plugin) for plugin in sorted_tool_plugins]

    @classmethod
    def filter_plugins_by_dependencies(
        cls,
        plugins: List['ProjectPluginEnum'],
    ):
        """
        Отфильтровывает плагины, у которых нехватает зависимостей
        """
        plugins = deepcopy(plugins)
        plugins_dependencies = cls.get_plugins_dependencies()

        for dependency_plugin, required_plugins in plugins_dependencies.items():
            if dependency_plugin in plugins:
                if required_plugins:
                    is_activated_all_required_plugins = all(
                        required_plugin in plugins
                        for required_plugin in required_plugins
                    )
                else:
                    is_activated_all_required_plugins = True

                if not is_activated_all_required_plugins:
                    plugins.remove(dependency_plugin)

        sorted_plugins = cls.sort_plugins_by_dependencies(plugins)

        return sorted_plugins

    @classmethod
    def get_project_plugins(cls, project: ProjectEnum) -> Tuple['ProjectPluginEnum']:
        """
        Возвращает набор плагинов проекта
        """
        get_plugins_method = getattr(cls, f'get_{project.short()}_plugins')

        return tuple(get_plugins_method())

    @classmethod
    def get_projects_plugins(
        cls,
        projects_combination: Tuple[ProjectEnum],
        only_base: bool,
    ):
        """
        Возвращает список плагинов для комбинации проектов. Так же учитываются зависимости плагинов, без которых они
        не смогут работать
        """
        plugins = cls.get_general_plugins(
            only_base=only_base,
        )

        for project in projects_combination:
            get_project_plugins = getattr(cls, f'get_{project.short()}_plugins')

            project_plugins = get_project_plugins(only_base=only_base)

            for project_plugin in project_plugins:
                plugins.append(project_plugin)

                # Дополнительно должны быть добавлены плагины, от которых зависит добавляемый. Иначе, приложение не
                # будет работоспособным
                cls.get_plugin_dependencies(
                    plugin=project_plugin,
                    plugin_dependencies=plugins
                )

        filtered_plugins = cls.filter_plugins_by_dependencies(
            plugins=plugins,
        )

        return filtered_plugins

    @classmethod
    def get_plugin_dependencies(cls, plugin: 'ProjectPluginEnum', plugin_dependencies: List['ProjectPluginEnum']):
        """
        Ищет и помещает зависимости плагина в список зависимостей
        """
        all_dependencies = cls.get_plugins_dependencies()

        for plugin_dependence in all_dependencies[plugin]:
            if plugin_dependence not in plugin_dependencies:
                plugin_dependencies.append(plugin_dependence)

                cls.get_plugin_dependencies(
                    plugin=plugin_dependence,
                    plugin_dependencies=plugin_dependencies,
                )

    @classmethod
    def get_enums_by_str_plugins(
        cls,
        plugins: Iterable[str],
        exclude_projects: Optional[Tuple[ProjectEnum]] = None,
    ) -> Tuple['ProjectPluginEnum']:
        """
        Преобразует строковые имена плагинов к перечислению
        """
        plugins = list(
            map(
                lambda plugin: (
                    getattr(cls, plugin.replace('.', '_').upper()) if
                    isinstance(plugin, str) else
                    plugin
                ),
                plugins
            )
        )

        if exclude_projects:
            exclude_plugins = tuple(chain(*[cls.get_project_plugins(project=project) for project in exclude_projects]))

            plugins = set(plugins).difference(exclude_plugins)

        return tuple(filter(None, plugins))

    @classmethod
    def get_projects_by_plugins(
        cls,
        plugins: Tuple['ProjectPluginEnum'],
    ) -> List[ProjectEnum]:
        """
        Получение списка проектов для набору плагинов
        """
        filtered_projects = []
        plugins_set = set(plugins)

        for project in ProjectEnum.get_projects():
            get_project_plugins = getattr(cls, f'get_{project.short()}_plugins')

            has_project = bool(
                plugins_set.intersection(get_project_plugins())
            )

            if has_project:
                filtered_projects.append(project)

        return filtered_projects

    @classmethod
    def get_project_combination_by_plugins(
        cls,
        plugins: Tuple['ProjectPluginEnum'],
        exclude_projects: Optional[Tuple[ProjectEnum]] = None,
    ) -> List[Tuple['ProjectEnum']]:
        """
        Получение допустимых комбинаций проектов для переданного списка плагинов
        """
        projects = cls.get_projects_by_plugins(
            plugins=plugins,
        )

        if exclude_projects:
            projects = tuple(set(projects).difference(exclude_projects))

        projects_combinations = ProjectEnum.get_projects_combinations(
            projects=tuple(projects),
        )

        return projects_combinations

    @classmethod
    def get_filtered_plugins_for_projects_combination(
        cls,
        projects_combination: Iterable[ProjectEnum],
        plugins: Iterable['ProjectPluginEnum'],
        with_test_plugins: bool = False,
    ) -> List['ProjectPluginEnum']:
        """
        Возвращает отфильтрованный список плагинов согласно комбинации проектов
        """
        filtered_plugins = []

        plugins = list(plugins)
        projects_combination = list(projects_combination)

        if with_test_plugins:
            plugins.extend(cls.get_behave_plugins())
            projects_combination.append(ProjectEnum.WEB_BB_BEHAVE)

        plugins_set = set(plugins)

        general_plugins_intersection = (
            plugins_set.intersection(cls.get_general_plugins())
        )

        if general_plugins_intersection:
            filtered_plugins.extend(general_plugins_intersection)

        for project in projects_combination:
            get_project_plugins = getattr(cls, f'get_{project.short()}_plugins')

            plugins_intersection = (
                plugins_set.intersection(get_project_plugins())
            )

            if plugins_intersection:
                filtered_plugins.extend(plugins_intersection)

        filtered_plugins = cls.filter_plugins_by_dependencies(
            plugins=filtered_plugins,
        )

        return filtered_plugins
