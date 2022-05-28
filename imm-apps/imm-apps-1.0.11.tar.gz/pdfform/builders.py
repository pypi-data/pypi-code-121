from pdfform import context
from datetime import date
from typing import Union

from .application_form import ApplicationForm
from . import option_lists

from model.common.cor import CORs
from model.common.id import ID, IDs
from model.common.address import Address, Addresses
from model.common.phone import Phone, Phones
from model.common.educationbase import EducationBase, EducationHistory
from model.tr.m5710 import TrBackground


def special_YMD_handle(the_date, form):
    the_date = the_date.strftime("%Y-%m-%d") if type(the_date) == date else the_date
    year, month, day = the_date.split("-")
    form.add_text(year)
    form.add_text(month)
    form.add_text(day)


def add_header(form: ApplicationForm, form_type: str = "1295"):
    """Add header section items"""
    personal = form.applicant.personal

    form.add_text(personal.uci)
    if form_type == "1295":
        form.add_dropdown(
            form.applicant.trcase.service_in, option_lists.service_language
        )
    else:
        form.add_dropdown(
            form.applicant.trcasein.service_in, option_lists.service_language
        )

    if form_type == "5708":
        if (
            form.applicant.vrincanada.application_purpose
            == "apply or extend visitor record"
        ):
            form.add_checkbox(True)
        else:
            form.add_skip(1)
        if form.applicant.vrincanada.application_purpose == "restore status as visotor":
            form.add_checkbox(True)
        else:
            form.add_skip(1)
        if form.applicant.vrincanada.application_purpose == "TRP":
            form.add_checkbox(True)
        else:
            form.add_skip(1)
    elif form_type == "5709":
        if (
            form.applicant.spincanada.application_purpose
            == "apply or extend study permit"
        ):
            form.add_checkbox(True)
        else:
            form.add_skip(1)
        if form.applicant.spincanada.application_purpose == "restore status as student":
            form.add_checkbox(True)
        else:
            form.add_skip(1)
        if form.applicant.spincanada.application_purpose == "TRP":
            form.add_checkbox(True)
        else:
            form.add_skip(1)
    elif form_type == "5710":
        # apply WP for same employer, apply WP for new employer,restore status as worker,, TRP with new employer
        if form.applicant.wpincanada.application_purpose == "restore status as worker":
            form.add_checkbox(True)  # pick apply for wp with same employer
            form.add_skip(1)
            form.add_checkbox(True)  # pick restore status
            form.add_skip(1)
        elif form.applicant.wpincanada.application_purpose == "TRP with same employer":
            form.add_checkbox(True)  # pick apply for wp with same employer
            form.add_skip(2)
            form.add_checkbox(True)  # pick restore status
        elif form.applicant.wpincanada.application_purpose == "TRP with new employer":
            form.add_skip(1)
            form.add_checkbox(True)  # pick apply for wp with same employer
            form.add_skip(1)
            form.add_checkbox(True)  # pick restore status
        else:
            if (
                form.applicant.wpincanada.application_purpose
                == "apply WP for same employer"
            ):
                form.add_checkbox(True)
                form.add_skip(3)
            else:
                form.add_skip(1)
            if (
                form.applicant.wpincanada.application_purpose
                == "apply WP for new employer"
            ):
                form.add_checkbox(True)
                form.add_skip(2)


def add_personal_detail(form: ApplicationForm, form_type: str = ""):
    """Add personal detail items
    1. full name
    2. other name
    3. sex
    4. date of birth
    5. place of birth
    6. citizenship
    7. current country or territory of residence
    8. previous countries or territories of residence
    9. country or territory where applying
    10. current marital status
    11. previous mariage
    """
    personal = form.applicant.personal
    form.add_info("personal detail section")

    form.add_text(personal.last_name)
    form.add_text(personal.first_name)

    if personal.used_first_name:
        form.add_radio(True)
        form.add_text(personal.used_last_name)
        form.add_text(personal.used_first_name)
    else:
        form.add_radio(False)
        form.add_skip(2)

    form.add_dropdown(personal.sex, option_lists.gender)

    form.add_date(personal.dob)

    form.add_text(personal.place_of_birth)
    form.add_dropdown(personal.country_of_birth, option_lists.country_of_birth)

    form.add_dropdown(personal.citizen, option_lists.country_of_citizen)

    # residence
    residence = CORs(form.applicant.cor).current
    form.add_dropdown(residence.country, option_lists.country_of_residence)
    status = residence.status
    form.add_dropdown(status, option_lists.immigration_status)
    if status.lower() in ["visitor", "worker", "student"]:
        form.add_skip(1)
        form.add_date(residence.start_date)
        form.add_date(residence.end_date)
    elif status.lower() in ["other"]:
        form.add_text("")
        form.add_date(residence.start_date)
        form.add_date(residence.end_date)
    else:
        form.add_skip(3)

    # previous residence
    previous_cors = CORs(form.applicant.cor).previous
    if previous_cors and len(previous_cors) > 0:
        p1 = previous_cors[0]
        p2 = previous_cors[1] if len(previous_cors) > 1 else None

        form.add_radio(True)
        form.add_dropdown(p1.country, option_lists.country_of_residence)
        form.add_dropdown(p1.status, option_lists.immigration_status)
        form.add_skip(1)
        form.add_date(p1.start_date)
        form.add_date(p1.end_date)

        if p2:
            form.add_dropdown(p2.country, option_lists.country_of_residence)
            form.add_dropdown(p2.status, option_lists.immigration_status)
            form.add_skip(1)
            form.add_date(p2.start_date)
            form.add_date(p2.end_date)
        else:
            form.add_skip(5)
    else:
        form.add_radio(False)
        form.add_skip(10)

    if form_type == "1295":
        if not form.applicant.trcase.same_as_cor:
            form.add_radio(False)
            tr = form.applicant.trcase
            form.add_dropdown(tr.applying_country, option_lists.previous_country)
            form.add_dropdown(tr.applying_status, option_lists.immigration_status)
            if tr.applying_status == "Other":
                form.add_text(tr.other_explain)
            else:
                form.add_skip(1)
            form.add_date(tr.applying_start_date)
            form.add_date(tr.applying_end_date)

        else:
            form.add_radio(True)
            form.add_skip(5)

    marriage = form.applicant.marriage
    status = marriage.marital_status

    form.add_dropdown(status, option_lists.marital_status, True)
    if status.lower() in ["married", "common-law"]:
        form.add_date(marriage.married_date)
        form.add_text(marriage.sp_last_name)
        form.add_text(marriage.sp_first_name)
        if form_type != "1295":
            form.add_radio(marriage.sp_is_canadian)
    else:
        form.add_skip(3 if form_type == "1295" else 4)

    if marriage.previous_married:
        form.add_radio(True)
        form.add_text(marriage.pre_sp_last_name)
        form.add_text(marriage.pre_sp_first_name)
        form.add_dropdown(marriage.pre_relationship_type, option_lists.relation_type)
        form.add_date(marriage.pre_start_date)
        form.add_date(marriage.pre_end_date)
        # speciaially dealing with
        special_YMD_handle(marriage.pre_sp_dob, form)

    else:
        form.add_radio(False)
        form.add_skip(8)


def add_language(form: ApplicationForm):
    """Add language items
    1. native language
    """
    form.add_info("language section")

    form.add_dropdown(
        form.applicant.personal.native_language, option_lists.native_language
    )
    form.add_dropdown(
        form.applicant.personal.english_french, option_lists.communication_language
    )
    if form.applicant.personal.english_french.lower() == "both":
        form.add_text(form.applicant.personal.which_one_better)
    else:
        form.add_skip(1)
    if form.applicant.personal.language_test:
        form.add_radio(True)
    else:
        form.add_radio(False)


def add_passport(form: ApplicationForm):
    """Add passport items
    1. passport number
    2. issue country`
    3. issue date
    4. expiry date
    5. Taiwan
    6. Israeli
    """
    form.add_info("passport section")

    passport: ID = IDs(form.applicant.personid).passport
    form.add_text(passport.number)
    form.add_dropdown(passport.country, option_lists.passport_issue_country, True)
    form.add_date(passport.issue_date)
    form.add_date(passport.expiry_date)

    if "taiwan" in passport.country.lower():
        form.add_radio(True)
    else:
        form.add_skip(1)
    if "israel" in passport.country.lower():
        form.add_radio(True)
    else:
        form.add_skip(1)


def add_national_id(form: ApplicationForm):
    """Add national id items
    1. if has national id
    2. id number
    3. issue country
    4. issue date
    5. expiry date
    """

    form.add_info("national id section")
    national_id: ID = IDs(form.applicant.personid).national_id
    if national_id.number:
        form.add_radio(True)
        form.add_text(national_id.number)
        form.add_dropdown(
            national_id.country, option_lists.passport_issue_country, True
        )
        if national_id.issue_date:
            form.add_date(national_id.issue_date)
        else:
            form.add_skip(1)
        if national_id.expiry_date:
            form.add_date(national_id.expiry_date)
        else:
            form.add_skip(1)
    else:
        form.add_radio(False)
        form.add_skip(4)


def add_uspr_card(form: ApplicationForm):
    form.add_info("US PR card section")

    """Add US PR card items"""
    pr: ID = IDs(form.applicant.personid).pr
    if pr.country and (
        "united states" in pr.country.lower() or "usa" in pr.country.lower()
    ):
        form.add_radio(True)
        form.add_text(pr.number)
        form.add_date(pr.expiry_date)
    else:
        form.add_radio(False)
        form.add_skip(2)


def add_contact_information(form: ApplicationForm, form_type: str = "1295"):
    """Add contact information"""

    form.add_info("contact information section")

    address: Address = Addresses(form.applicant.address).mailing
    residential_address: Address = Addresses(form.applicant.address).residential

    form.add_text(address.po_box)
    form.add_text(address.unit)
    form.add_text(address.street_number)
    form.add_text(address.street_name)
    form.add_text(address.city)
    country = address.country
    form.add_dropdown(country, option_lists.mailing_country)
    if country.lower() == "canada":
        form.add_dropdown(address.province, option_lists.canada_province)
    else:
        form.add_skip(1)
    form.add_text(address.post_code)
    if form_type == "1295":
        form.add_text(address.district)

    if residential_address != address:
        form.add_radio(False)
        form.add_text(residential_address.unit)
        form.add_text(residential_address.street_number)
        form.add_text(residential_address.street_name)
        form.add_text(residential_address.city)
        country = residential_address.country
        form.add_dropdown(country, option_lists.mailing_country)
        if country.lower() == "canada":
            form.add_dropdown(
                residential_address.province, option_lists.canada_province
            )
        else:
            form.add_skip(1)
        form.add_text(residential_address.post_code)
        if form_type == "1295":
            form.add_text(residential_address.district)

    else:
        form.add_radio(True)
        if form_type == "1295":
            form.add_skip(8)
        else:
            form.add_skip(7)

    # telephone
    telephone: Union[Phone, None] = Phones(form.applicant.phone).PreferredPhone
    if telephone and telephone.isCanadaUs:
        pause = 0.5  # this place could be easily erred
        form.add_checkbox(True)
        form.add_skip(1)
        form.add_dropdown(telephone.variable_type.title(), option_lists.telephone_type)
        form.add_skip(1)
        if form_type == "1295":  # try to work around 1295 tab order issue
            form.add_text(telephone.ext, pause=pause)
            form.add_text(telephone.number, pause=pause)
            form.add_skip(3)
        else:
            # when a valid Canada phone number finished, it will automatically tab to next control
            ext = telephone.ext if telephone.ext else ""
            form.add_text(telephone.number + ext, pause=pause)

    else:
        pause = 0.1
        form.add_skip(1)
        form.add_checkbox(True)
        form.add_dropdown(telephone.variable_type.title(), option_lists.telephone_type)
        form.add_text(telephone.country_code, pause=pause)
        form.add_text(telephone.number, pause=pause)
        form.add_text(telephone.ext, pause=pause)
    # alternative phone or fax is not used usually, ignore alternate telephone and fax
    form.add_skip(11)

    form.add_text(form.applicant.personal.email)


def add_coming_into_canada(form: ApplicationForm):
    """Add coming into canada."""

    form.add_info("coming into Canada section")

    coming = form.applicant.trcasein
    form.add_date(coming.original_entry_date)
    form.add_text(coming.original_entry_place)
    form.add_dropdown(coming.original_purpose, option_lists.purpose_of_coming)

    if coming.original_purpose == "Other":
        form.add_text(coming.original_other_reason)
    else:
        form.add_skip(1)

    if coming.most_recent_entry_date:
        form.add_date(coming.most_recent_entry_date)
        form.add_text(coming.most_recent_entry_place)
        form.add_text(coming.doc_number)
    else:
        form.add_skip(3)


def add_work_detail(form: ApplicationForm, form_type: str = "1295"):
    """Add details of intended work in Canada"""

    form.add_info("intended work section")

    work_detail = (
        form.applicant.wp if form_type == "1295" else form.applicant.wpincanada
    )
    if form_type == "5710":
        form.add_dropdown(work_detail.work_permit_type, option_lists.work_permit_ex)
        if work_detail.work_permit_type == "Other":
            form.add_text(work_detail.other_explain)
        else:
            form.add_skip(1)
    else:
        form.add_dropdown(work_detail.work_permit_type, option_lists.work_permit)

    if work_detail.employer_name:
        form.add_text(work_detail.employer_name)
    else:
        form.add_text("Not applicable")

    if work_detail.employer_name:
        form.add_text(work_detail.employer_address)
    else:
        form.add_text("Not applicable")

    province = work_detail.work_province
    if province:
        form.add_dropdown(province, option_lists.canada_province)
    else:
        form.add_skip(1)

    if work_detail.work_city:
        form.add_dropdown(
            work_detail.work_city.upper(), option_lists.canada_province_cities[province]
        )
    else:
        form.add_skip(1)

    if work_detail.employer_address:
        form.add_text(work_detail.employer_address)
    else:
        form.add_text("TO BE DETERMINED")

    if work_detail.job_title:
        form.add_text(work_detail.job_title)
    else:
        form.add_text("TO BE DETERMINED")

    if work_detail.brief_duties:
        form.add_text(work_detail.brief_duties)
    else:
        form.add_text("TO BE DETERMINED")

    if work_detail.duration_from:
        form.add_date(work_detail.duration_from)
    else:
        form.add_skip(1)

    if work_detail.duration_to:
        form.add_date(work_detail.duration_to)
    else:
        form.add_skip(1)

    if work_detail.lmia_num_or_offer_num:
        form.add_text(work_detail.lmia_num_or_offer_num)
    else:
        form.add_skip(1)

    if form_type == "5710":
        if work_detail.caq_number:
            form.add_text(work_detail.caq_number)
            form.add_date(work_detail.expiry_date)
        else:
            form.add_skip(2)
        form.add_radio(work_detail.pnp_certificated)


def add_visit_detail(form: ApplicationForm):
    """Add visit details"""
    form.add_info("details of visit section")

    visit = form.applicant.vrincanada
    form.add_dropdown(visit.visit_purpose, option_lists.purpose_of_vist)
    if visit.visit_purpose.lower() == "other":
        form.add_text(visit.other_explain)
    else:
        form.add_skip(1)
    form.add_date(visit.duration_from)
    form.add_date(visit.duration_to)
    form.add_text(str(visit.funds_available))
    form.add_dropdown(visit.paid_by, option_lists.expense_by)
    if visit.paid_by.lower() == "other":
        form.add_text(visit.other_payer_explain)
    else:
        form.add_skip(1)

    form.add_text(visit.name1)
    form.add_text(visit.relationship1)
    form.add_text(visit.address1)
    form.add_text(visit.name2)
    form.add_text(visit.relationship2)
    form.add_text(visit.address2)


def add_study_detail(form: ApplicationForm):
    """Add study details"""
    form.add_info("details of study section")

    detail = form.applicant.spincanada
    form.add_text(detail.school_name)
    form.add_dropdown(
        option_lists.get_5709_study_level(detail.study_level),
        option_lists.level_of_study,
    )
    form.add_dropdown(detail.study_field, option_lists.field_of_study, True)

    form.add_dropdown(detail.province, option_lists.canada_province)
    form.add_dropdown(
        detail.city.upper(), option_lists.canada_province_cities[detail.province]
    )
    form.add_text(detail.address)
    form.add_text(detail.dli)
    form.add_text(detail.student_id)
    form.add_date(detail.duration_from)
    form.add_date(detail.duration_to)

    form.add_text(detail.tuition_cost)
    form.add_text(detail.room_cost)
    form.add_text(detail.other_cost)
    form.add_text(detail.fund_available)
    form.add_dropdown(detail.paid_person, option_lists.expense_by)
    form.add_skip(1)
    form.add_radio(detail.apply_work_permit)
    if detail.apply_work_permit:
        form.add_dropdown(detail.work_permit_type, option_lists.work_permit_student)
        form.add_text(detail.caq_number)
        form.add_text(detail.expiry_date)
    else:
        form.add_skip(3)


def add_education(form: ApplicationForm):
    """Add education"""
    form.add_info("education section")

    education: Union[EducationBase, None] = EducationHistory(
        form.applicant.education
    ).highestEducation
    if education and education.level_in_num >= 2:  # >=2 means post secondary
        form.add_radio(True)
        form.add_date(education.start_date, True)
        form.add_text(education.field_of_study)
        form.add_text(education.school_name)
        form.add_date(education.end_date, True)
        form.add_text(education.city)
        country = education.country
        form.add_dropdown(country, option_lists.country_of_birth)
        if country and country.lower() == "canada":
            form.add_dropdown(education.province, option_lists.canada_province)
        else:
            form.add_skip(1)
    else:
        form.add_radio(False)
        form.add_skip(9)


def add_employment(form: ApplicationForm, form_type: str = "1295"):
    """Add employment"""
    form.add_info("employment section")

    slots = 3  # num of slots in form
    if form.applicant.employment:
        employments = form.applicant.employment
        for employment in employments:
            # WTF!! work around the form bug
            if slots == 2 and form_type == "1295":
                year, month, day = employment.start_date.strftime("%Y-%m-%d").split("-")
                form.add_text(year)
                form.add_text(month)
            else:
                form.add_date(employment.start_date, True)
            form.add_text(employment.job_title)
            form.add_text(employment.company)
            form.add_date(employment.end_date, True)
            form.add_text(employment.city)
            country = employment.country
            form.add_dropdown(country, option_lists.country_of_birth)
            if country.lower() == "canada":
                form.add_dropdown(employment.province, option_lists.canada_province)
            else:
                form.add_skip(1)
            slots -= 1
            if slots == 0:
                break

    # skip emply slots
    for _ in range(slots):
        form.add_skip(9)


def add_background(form: ApplicationForm):
    """Add background information"""
    form.add_info("background information section")

    background: TrBackground = form.applicant.trbackground
    form.add_radio(background.q1a)
    form.add_radio(background.q1b)
    if background.q1a or background.q1b:
        form.add_text(background.q1c)
    else:
        form.add_skip(1)

    form.add_radio(background.q2a)
    form.add_radio(background.q2b)
    form.add_radio(background.q2c)
    if background.q2a or background.q2b or background.q2c:
        form.add_text(background.q2d)
    else:
        form.add_skip(1)

    form.add_radio(background.q3a)
    if background.q3a:
        form.add_text(background.q3b)
    else:
        form.add_skip(1)

    form.add_radio(background.q4a)
    if background.q4a:
        form.add_text(background.q4b)
    else:
        form.add_skip(1)

    form.add_radio(background.q5)

    form.add_radio(background.q6)


def add_signature(form: ApplicationForm):
    """Add signature section"""
    form.add_radio(True)

    form.add_text(
        f"{form.applicant.personal.last_name} {form.applicant.personal.first_name}"
    )  # signature
    form.add_text(str(date.today()))


def build_form_1295(applicant: dict) -> ApplicationForm:
    """Build form 1295 with Applicant data

    Args:
        applicant: applicant data dict

    Returns:
        ApplicationForm of 1295
    """
    print("Build form 1295")

    form = ApplicationForm(applicant)

    # skip the top buttons
    form.add_skip(3)

    # Header section
    add_header(form)

    # Personal Details section
    add_personal_detail(form, "1295")

    # Language section
    add_language(form)

    # Passport section
    add_passport(form)

    # National Identity document section
    add_national_id(form)

    # US PR Card section
    add_uspr_card(form)

    # Contact Information section
    add_contact_information(form, "1295")

    # Details of intended work in Canada section #TODO:
    add_work_detail(form)

    # Education section
    add_education(form)

    # Employment section
    add_employment(form)

    form.add_info("skip clear section button")
    form.add_skip(1)  # skip Clear Section button

    # Background information section
    add_background(form)

    # Signature section
    add_signature(form)

    form.add_skip(1)  # skip infosource web link
    form.add_info("click validate button")
    form.add_button()

    return form


def build_form_5708(applicant: dict) -> ApplicationForm:
    form = ApplicationForm(applicant)

    # skip the top buttons
    form.add_skip(3)

    add_header(form, "5708")

    add_personal_detail(form)

    add_language(form)

    add_passport(form)

    add_national_id(form)

    add_uspr_card(form)

    add_contact_information(form, "5708")

    add_coming_into_canada(form)

    add_visit_detail(form)

    add_education(form)

    add_employment(form, "5708")

    form.add_info("skip clear section button")
    form.add_skip(1)  # skip Clear Section button

    # Background information section
    add_background(form)

    # Signature section
    add_signature(form)

    form.add_skip(1)  # skip infosource web link
    form.add_info("click validate button")
    form.add_button()

    return form


def build_form_5709(applicant: dict) -> ApplicationForm:
    form = ApplicationForm(applicant)

    # skip the top buttons
    form.add_skip(3)

    add_header(form, "5709")

    add_personal_detail(form)

    add_language(form)

    add_passport(form)

    add_national_id(form)

    add_uspr_card(form)

    add_contact_information(form, "5709")

    add_coming_into_canada(form)

    add_study_detail(form)

    add_education(form)

    add_employment(form, "5709")

    form.add_info("skip clear section button")
    form.add_skip(1)  # skip Clear Section button

    add_background(form)

    add_signature(form)

    form.add_skip(1)  # skip infosource web link
    form.add_info("click validate button")
    form.add_button()

    return form


def build_form_5710(applicant: dict) -> ApplicationForm:
    form = ApplicationForm(applicant)

    # skip the top buttons
    form.add_skip(3)

    add_header(form, "5710")

    add_personal_detail(form)

    add_language(form)

    add_passport(form)

    add_national_id(form)

    add_uspr_card(form)

    add_contact_information(form, "5710")

    add_coming_into_canada(form)

    add_work_detail(form, "5710")

    add_education(form)

    add_employment(form, "5710")

    form.add_info("skip clear section button")
    form.add_skip(1)  # skip Clear Section button

    add_background(form)

    add_signature(form)

    form.add_skip(1)  # skip infosource web link
    form.add_info("click validate button")
    form.add_button()

    return form


form_builder = {
    "1295": build_form_1295,
    "5708": build_form_5708,
    "5709": build_form_5709,
    "5710": build_form_5710,
}


def build_form(form_type: str, applicant: dict) -> ApplicationForm:
    return form_builder[form_type](applicant)
