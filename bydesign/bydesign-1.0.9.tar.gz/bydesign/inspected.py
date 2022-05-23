# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class BiAutoship(models.Model):
    rep_field = models.CharField(db_column='Rep #', max_length=20, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    customerid = models.IntegerField(db_column='CustomerID')  # Field name made lowercase.
    bcid = models.IntegerField(db_column='BCID')  # Field name made lowercase.
    autoshipscheduleid = models.IntegerField(db_column='AutoshipScheduleID')  # Field name made lowercase.
    autoshipperiodtypeid = models.IntegerField(db_column='AutoshipPeriodTypeID')  # Field name made lowercase.
    period_unit = models.IntegerField(db_column='Period Unit')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    startdate = models.DateTimeField(db_column='StartDate')  # Field name made lowercase.
    stopdate = models.DateTimeField(db_column='StopDate')  # Field name made lowercase.
    datenextrun = models.DateTimeField(db_column='DateNextRun')  # Field name made lowercase.
    autoshipruleid = models.IntegerField(db_column='AutoshipRuleID', blank=True, null=True)  # Field name made lowercase.
    shipmethodid = models.IntegerField(db_column='ShipMethodID', blank=True, null=True)  # Field name made lowercase.
    shipname1 = models.CharField(db_column='ShipName1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipname2 = models.CharField(db_column='ShipName2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipphone = models.CharField(db_column='ShipPhone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    creditcardprofileid = models.IntegerField(db_column='CreditCardProfileID', blank=True, null=True)  # Field name made lowercase.
    achprofileid = models.IntegerField(db_column='ACHProfileID', blank=True, null=True)  # Field name made lowercase.
    checkdraftprofileid = models.IntegerField(db_column='CheckDraftProfileID', blank=True, null=True)  # Field name made lowercase.
    orderid = models.IntegerField(db_column='OrderID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_autoship'


class BiAutoshipdetails(models.Model):
    autoshipscheduleid = models.IntegerField(db_column='AutoshipScheduleID')  # Field name made lowercase.
    autoshipdetailid = models.IntegerField(db_column='AutoShipDetailID')  # Field name made lowercase.
    inventoryid = models.IntegerField(db_column='InventoryID')  # Field name made lowercase.
    groupitem = models.SmallIntegerField(db_column='GroupItem', blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_autoshipdetails'


class BiAutoshipperiodtypes(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=25, blank=True, null=True)  # Field name made lowercase.
    explanation = models.CharField(db_column='Explanation', max_length=150, blank=True, null=True)  # Field name made lowercase.
    repextdescription = models.CharField(db_column='RepExtDescription', max_length=100, blank=True, null=True)  # Field name made lowercase.
    custextdescription = models.CharField(db_column='CustExtDescription', max_length=100, blank=True, null=True)  # Field name made lowercase.
    datepart = models.TextField(db_column='DatePart')  # Field name made lowercase.
    increment = models.SmallIntegerField(db_column='Increment')  # Field name made lowercase.
    useperiodday = models.SmallIntegerField(db_column='UsePeriodDay')  # Field name made lowercase.
    isactive = models.SmallIntegerField(db_column='IsActive')  # Field name made lowercase.
    isallowextranetedit = models.SmallIntegerField(db_column='IsAllowExtranetEdit')  # Field name made lowercase.
    isrepextallowselection = models.SmallIntegerField(db_column='IsRepExtAllowSelection')  # Field name made lowercase.
    iscustextallowselection = models.SmallIntegerField(db_column='IsCustExtAllowSelection')  # Field name made lowercase.
    isallowexteditpayments = models.SmallIntegerField(db_column='IsAllowExtEditPayments', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_autoshipperiodtypes'


class BiBonusBonusdetails(models.Model):
    bonusdetailid = models.IntegerField(db_column='BonusDetailID')  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    payonrepid = models.CharField(db_column='PayOnRepID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bonusrunid = models.IntegerField(db_column='BonusRunID')  # Field name made lowercase.
    bonustypeid = models.IntegerField(db_column='BonusTypeID', blank=True, null=True)  # Field name made lowercase.
    orderid = models.IntegerField(db_column='OrderID')  # Field name made lowercase.
    bonustypereportingvalue1 = models.DecimalField(db_column='BonusTypeReportingValue1', max_digits=18, decimal_places=6)  # Field name made lowercase.
    bonustypereportingvalue2 = models.DecimalField(db_column='BonusTypeReportingValue2', max_digits=18, decimal_places=6)  # Field name made lowercase.
    bonustypereportingvalue3 = models.DecimalField(db_column='BonusTypeReportingValue3', max_digits=18, decimal_places=6)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_bonus_bonusdetails'


class BiBonusBonusrun(models.Model):
    bonus_run_field = models.IntegerField(db_column='Bonus Run #')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    bonus_description = models.CharField(db_column='Bonus Description', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    periodstartdate = models.DateTimeField(db_column='PeriodStartDate')  # Field name made lowercase.
    periodenddate = models.DateTimeField(db_column='PeriodEndDate')  # Field name made lowercase.
    qualifystartdate = models.DateTimeField(db_column='QualifyStartDate', blank=True, null=True)  # Field name made lowercase.
    qualifyenddate = models.DateTimeField(db_column='QualifyEndDate', blank=True, null=True)  # Field name made lowercase.
    payout_field = models.IntegerField(db_column='Payout #')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'bi_bonus_bonusrun'


class BiBonusDynamicearnings(models.Model):
    rep_field = models.CharField(db_column='Rep #', max_length=20, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    pay_on_rep_field = models.CharField(db_column='Pay On Rep#', max_length=20, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    bonus_run_field = models.IntegerField(db_column='Bonus Run#')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    bonus_type = models.CharField(db_column='Bonus Type', max_length=100, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    periodstartdate = models.DateTimeField(db_column='PeriodStartDate')  # Field name made lowercase.
    periodenddate = models.DateTimeField(db_column='PeriodEndDate')  # Field name made lowercase.
    bonus_amount = models.DecimalField(db_column='Bonus Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'bi_bonus_dynamicearnings'


class BiBonusPayouts(models.Model):
    rep_field = models.CharField(db_column='Rep #', max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    prev_balance_forward = models.DecimalField(db_column='Prev Balance Forward', max_digits=19, decimal_places=4)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    adjustments = models.DecimalField(db_column='Adjustments', max_digits=19, decimal_places=4)  # Field name made lowercase.
    bonus_amount = models.DecimalField(db_column='Bonus Amount', max_digits=19, decimal_places=4)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    amount_pre_field = models.DecimalField(db_column='Amount (Pre)', max_digits=19, decimal_places=4)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    currency_pre_field = models.CharField(db_column='Currency (Pre)', max_length=10)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    amount_post_field = models.DecimalField(db_column='Amount (Post)', max_digits=19, decimal_places=4)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    currency_post_field = models.CharField(db_column='Currency (Post)', max_length=10)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    balance_forward = models.DecimalField(db_column='Balance Forward', max_digits=19, decimal_places=4)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    payout_field = models.IntegerField(db_column='Payout #')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    payout_description = models.CharField(db_column='Payout Description', max_length=250, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    payout_method = models.CharField(db_column='Payout Method', max_length=50)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    payout_fee = models.DecimalField(db_column='Payout Fee', max_digits=19, decimal_places=4)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ref_field = models.IntegerField(db_column='Ref #')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    date_created = models.DateTimeField(db_column='Date Created')  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'bi_bonus_payouts'


class BiBonusagentgroups(models.Model):
    bonusgroupid = models.IntegerField(db_column='BonusGroupID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_bonusagentgroups'


class BiBonusagents(models.Model):
    bonusagentid = models.IntegerField(db_column='BonusAgentID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    configurationid = models.IntegerField(db_column='ConfigurationID')  # Field name made lowercase.
    bonusagentgroupid = models.IntegerField(db_column='BonusAgentGroupID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_bonusagents'


class BiBonusdetails(models.Model):
    bonusdetailid = models.IntegerField(db_column='BonusDetailID')  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    payonrepid = models.CharField(db_column='PayOnRepID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bonusrunid = models.IntegerField(db_column='BonusRunID')  # Field name made lowercase.
    bonustypeid = models.IntegerField(db_column='BonusTypeID')  # Field name made lowercase.
    orderid = models.IntegerField(db_column='OrderID')  # Field name made lowercase.
    bonustypereportingvalue1 = models.DecimalField(db_column='BonusTypeReportingValue1', max_digits=18, decimal_places=6)  # Field name made lowercase.
    bonustypereportingvalue2 = models.DecimalField(db_column='BonusTypeReportingValue2', max_digits=18, decimal_places=6)  # Field name made lowercase.
    bonustypereportingvalue3 = models.DecimalField(db_column='BonusTypeReportingValue3', max_digits=18, decimal_places=6)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_bonusdetails'


class BiBonusruns(models.Model):
    bonusrunid = models.IntegerField(db_column='BonusRunID')  # Field name made lowercase.
    bonus_description = models.CharField(db_column='Bonus Description', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    periodstartdate = models.DateTimeField(db_column='PeriodStartDate')  # Field name made lowercase.
    periodenddate = models.DateTimeField(db_column='PeriodEndDate')  # Field name made lowercase.
    qualifystartdate = models.DateTimeField(db_column='QualifyStartDate', blank=True, null=True)  # Field name made lowercase.
    qualifyenddate = models.DateTimeField(db_column='QualifyEndDate', blank=True, null=True)  # Field name made lowercase.
    payoutprocessid = models.IntegerField(db_column='PayoutProcessID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_bonusruns'


class BiBonustypes(models.Model):
    bonusagentid = models.IntegerField(db_column='BonusAgentID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    periodcalendar = models.CharField(db_column='PeriodCalendar', max_length=200, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_bonustypes'


class BiCompconfigurations(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    version = models.IntegerField(db_column='Version', blank=True, null=True)  # Field name made lowercase.
    signoffversion = models.CharField(db_column='SignoffVersion', max_length=10, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_compconfigurations'


class BiCompmatrixdata(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    compentityid = models.IntegerField(db_column='CompEntityID')  # Field name made lowercase.
    compentitytypeid = models.IntegerField(db_column='CompEntityTypeID')  # Field name made lowercase.
    dependentcomprankid = models.IntegerField(db_column='DependentCompRankID', blank=True, null=True)  # Field name made lowercase.
    dependentcompqualagentid = models.IntegerField(db_column='DependentCompQualAgentID', blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    generation = models.IntegerField(db_column='Generation', blank=True, null=True)  # Field name made lowercase.
    minamount = models.DecimalField(db_column='MinAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    maxamount = models.DecimalField(db_column='MaxAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    value1 = models.DecimalField(db_column='Value1', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    value2 = models.DecimalField(db_column='Value2', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_compmatrixdata'


class BiCompranks(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=1000)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10)  # Field name made lowercase.
    compconfigurationid = models.IntegerField(db_column='CompConfigurationID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_compranks'


class BiCurrencies(models.Model):
    currencyid = models.IntegerField(db_column='CurrencyID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10)  # Field name made lowercase.
    active = models.SmallIntegerField(db_column='Active')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_currencies'


class BiCustomers(models.Model):
    customerid = models.IntegerField(db_column='CustomerID')  # Field name made lowercase.
    customer_field = models.CharField(db_column='Customer #', max_length=20, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    middleinitial = models.CharField(db_column='MiddleInitial', max_length=1, blank=True, null=True)  # Field name made lowercase.
    joindate = models.DateTimeField(db_column='JoinDate')  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstreet1 = models.CharField(db_column='BillStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstreet2 = models.CharField(db_column='BillStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcity = models.CharField(db_column='BillCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcounty = models.CharField(db_column='BillCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstate = models.CharField(db_column='BillState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billpostalcode = models.CharField(db_column='BillPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcountry = models.CharField(db_column='BillCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dateofbirth = models.DateTimeField(db_column='DateOfBirth', blank=True, null=True)  # Field name made lowercase.
    customertypeid = models.IntegerField(db_column='CustomerTypeID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_customers'


class BiCustomertypes(models.Model):
    customertypeid = models.IntegerField(db_column='CustomerTypeID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_customertypes'


class BiInventory(models.Model):
    inventoryid = models.IntegerField(db_column='InventoryID')  # Field name made lowercase.
    item_field = models.CharField(db_column='Item #', max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    explanation = models.CharField(db_column='Explanation', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    taxcode = models.CharField(db_column='TaxCode', max_length=25)  # Field name made lowercase.
    isactive = models.SmallIntegerField(db_column='IsActive')  # Field name made lowercase.
    currencyid = models.IntegerField(db_column='CurrencyID')  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=100)  # Field name made lowercase.
    cost = models.DecimalField(db_column='Cost', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    featureditemreps = models.SmallIntegerField(db_column='FeaturedItemReps')  # Field name made lowercase.
    featureditemcustomers = models.SmallIntegerField(db_column='FeaturedItemCustomers')  # Field name made lowercase.
    outofstocklevel = models.IntegerField(db_column='OutOfStockLevel')  # Field name made lowercase.
    outofstockmessage = models.CharField(db_column='OutOfStockMessage', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    lowstocklevel = models.IntegerField(db_column='LowStockLevel')  # Field name made lowercase.
    lowstockmessage = models.CharField(db_column='LowStockMessage', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='SortOrder')  # Field name made lowercase.
    virtualitem = models.IntegerField(db_column='VirtualItem')  # Field name made lowercase.
    freeshipping = models.SmallIntegerField(db_column='FreeShipping')  # Field name made lowercase.
    shippingsurcharge = models.DecimalField(db_column='ShippingSurcharge', max_digits=19, decimal_places=4)  # Field name made lowercase.
    shippingsurchargebase = models.DecimalField(db_column='ShippingSurchargeBase', max_digits=19, decimal_places=4)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    groupitemoverrideweight = models.DecimalField(db_column='GroupItemOverrideWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    handlingfee = models.DecimalField(db_column='HandlingFee', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_inventory'


class BiInventorycategory(models.Model):
    categoryid = models.IntegerField(db_column='CategoryID')  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=100)  # Field name made lowercase.
    subcategory = models.CharField(db_column='SubCategory', max_length=100, blank=True, null=True)  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='SortOrder')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)  # Field name made lowercase.
    lastmodifiedby = models.CharField(db_column='LastModifiedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_inventorycategory'


class BiInventorycountry(models.Model):
    inventoryid = models.IntegerField(db_column='InventoryID')  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_inventorycountry'


class BiInventorygroups(models.Model):
    groupid = models.IntegerField(db_column='GroupID')  # Field name made lowercase.
    parentinventoryid = models.IntegerField(db_column='ParentInventoryID')  # Field name made lowercase.
    childinventoryid = models.IntegerField(db_column='ChildInventoryID')  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_inventorygroups'


class BiInventoryprices(models.Model):
    priceid = models.IntegerField(db_column='PriceID')  # Field name made lowercase.
    inventoryid = models.IntegerField(db_column='InventoryID')  # Field name made lowercase.
    ranktypeid = models.IntegerField(db_column='RanktypeID')  # Field name made lowercase.
    pricetext = models.CharField(db_column='PriceText', max_length=25)  # Field name made lowercase.
    currencyid = models.IntegerField(db_column='CurrencyID')  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume1 = models.DecimalField(db_column='Volume1', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume2 = models.DecimalField(db_column='Volume2', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume3 = models.DecimalField(db_column='Volume3', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume4 = models.DecimalField(db_column='Volume4', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice1 = models.DecimalField(db_column='OtherPrice1', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice2 = models.DecimalField(db_column='OtherPrice2', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice3 = models.DecimalField(db_column='OtherPrice3', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice4 = models.DecimalField(db_column='OtherPrice4', max_digits=19, decimal_places=4)  # Field name made lowercase.
    compare = models.DecimalField(db_column='Compare', max_digits=19, decimal_places=4)  # Field name made lowercase.
    taxableamount = models.DecimalField(db_column='TaxableAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate')  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)  # Field name made lowercase.
    lastmodifiedby = models.CharField(db_column='LastModifiedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    returnprice = models.DecimalField(db_column='ReturnPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    mup_qtystart = models.IntegerField(db_column='MUP_QtyStart')  # Field name made lowercase.
    mup_qtystop = models.IntegerField(db_column='MUP_QtyStop')  # Field name made lowercase.
    mup_qtyvalue = models.IntegerField(db_column='MUP_QtyValue')  # Field name made lowercase.
    shippingvalue = models.DecimalField(db_column='ShippingValue', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    vattax = models.DecimalField(db_column='VATTax', max_digits=19, decimal_places=4)  # Field name made lowercase.
    handlingfee = models.DecimalField(db_column='HandlingFee', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_inventoryprices'


class BiInventorywarehouse(models.Model):
    inventoryid = models.IntegerField(db_column='InventoryID')  # Field name made lowercase.
    warehouseid = models.IntegerField(db_column='WarehouseID')  # Field name made lowercase.
    onhand = models.IntegerField(db_column='OnHand')  # Field name made lowercase.
    reorderpoint = models.IntegerField(db_column='ReOrderPoint', blank=True, null=True)  # Field name made lowercase.
    onhandshipped = models.IntegerField(db_column='OnHandShipped')  # Field name made lowercase.
    cost = models.DecimalField(db_column='Cost', max_digits=19, decimal_places=4)  # Field name made lowercase.
    idealonhand = models.IntegerField(db_column='IdealOnHand')  # Field name made lowercase.
    avgweightedcost = models.DecimalField(db_column='AvgWeightedCost', max_digits=19, decimal_places=4)  # Field name made lowercase.
    packslipsortorder = models.IntegerField(db_column='PackSlipSortOrder')  # Field name made lowercase.
    outofstocklevel = models.IntegerField(db_column='OutOfStockLevel')  # Field name made lowercase.
    outofstockmessage = models.CharField(db_column='OutOfStockMessage', max_length=300, blank=True, null=True)  # Field name made lowercase.
    lowstocklevel = models.IntegerField(db_column='LowStockLevel')  # Field name made lowercase.
    lowstockmessage = models.CharField(db_column='LowStockMessage', max_length=300, blank=True, null=True)  # Field name made lowercase.
    packslipproductid = models.CharField(db_column='PackslipProductID', max_length=40, blank=True, null=True)  # Field name made lowercase.
    packslipdescription = models.CharField(db_column='PackslipDescription', max_length=200, blank=True, null=True)  # Field name made lowercase.
    softcount = models.IntegerField(db_column='SoftCount')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)  # Field name made lowercase.
    lastmodifiedby = models.CharField(db_column='LastModifiedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_inventorywarehouse'


class BiOrderdetails(models.Model):
    orderid = models.IntegerField(db_column='OrderID')  # Field name made lowercase.
    orderdetailid = models.IntegerField(db_column='OrderDetailID')  # Field name made lowercase.
    orderdetailstatusid = models.IntegerField(db_column='OrderDetailStatusID')  # Field name made lowercase.
    inventoryid = models.IntegerField(db_column='InventoryID')  # Field name made lowercase.
    groupitem = models.IntegerField(db_column='GroupItem')  # Field name made lowercase.
    groupownerdetailid = models.IntegerField(db_column='GroupOwnerDetailID')  # Field name made lowercase.
    packslipped = models.IntegerField(db_column='PackSlipped')  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')  # Field name made lowercase.
    volume1 = models.DecimalField(db_column='Volume1', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume2 = models.DecimalField(db_column='Volume2', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume3 = models.DecimalField(db_column='Volume3', max_digits=19, decimal_places=4)  # Field name made lowercase.
    volume4 = models.DecimalField(db_column='Volume4', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice1 = models.DecimalField(db_column='OtherPrice1', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice2 = models.DecimalField(db_column='OtherPrice2', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice3 = models.DecimalField(db_column='OtherPrice3', max_digits=19, decimal_places=4)  # Field name made lowercase.
    otherprice4 = models.DecimalField(db_column='OtherPrice4', max_digits=19, decimal_places=4)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=19, decimal_places=4)  # Field name made lowercase.
    tax = models.DecimalField(db_column='Tax', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    taxableamount = models.DecimalField(db_column='TaxableAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    compare = models.DecimalField(db_column='Compare', max_digits=19, decimal_places=4)  # Field name made lowercase.
    trackingid = models.CharField(db_column='TrackingID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    warehouseid = models.IntegerField(db_column='WarehouseID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_orderdetails'


class BiOrderdetailstatuses(models.Model):
    orderdetailstatusid = models.IntegerField(db_column='OrderDetailStatusID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    official = models.SmallIntegerField(db_column='Official')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_orderdetailstatuses'


class BiOrders(models.Model):
    orderid = models.IntegerField(db_column='OrderID')  # Field name made lowercase.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    bcid = models.IntegerField(db_column='BCID')  # Field name made lowercase.
    customerid = models.IntegerField(db_column='CustomerID')  # Field name made lowercase.
    partyid = models.IntegerField(db_column='PartyID', blank=True, null=True)  # Field name made lowercase.
    orderdate = models.DateTimeField(db_column='OrderDate')  # Field name made lowercase.
    bonusdate = models.DateTimeField(db_column='BonusDate')  # Field name made lowercase.
    dateshipped = models.DateTimeField(db_column='DateShipped', blank=True, null=True)  # Field name made lowercase.
    orderstatusid = models.IntegerField(db_column='OrderStatusID')  # Field name made lowercase.
    rankpricetypeid = models.IntegerField(db_column='RankPriceTypeID')  # Field name made lowercase.
    shipping = models.DecimalField(db_column='Shipping', max_digits=19, decimal_places=4)  # Field name made lowercase.
    handling = models.DecimalField(db_column='Handling', max_digits=19, decimal_places=4)  # Field name made lowercase.
    shippingtax = models.DecimalField(db_column='ShippingTax', max_digits=19, decimal_places=4)  # Field name made lowercase.
    handlingtax = models.DecimalField(db_column='HandlingTax', max_digits=19, decimal_places=4)  # Field name made lowercase.
    totalprice = models.DecimalField(db_column='TotalPrice', max_digits=19, decimal_places=4)  # Field name made lowercase.
    currencytypeid = models.IntegerField(db_column='CurrencyTypeID', blank=True, null=True)  # Field name made lowercase.
    billstreet1 = models.CharField(db_column='BillStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstreet2 = models.CharField(db_column='BillStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcity = models.CharField(db_column='BillCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcounty = models.CharField(db_column='BillCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstate = models.CharField(db_column='BillState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billpostalcode = models.CharField(db_column='BillPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcountry = models.CharField(db_column='BillCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dateposted = models.DateTimeField(db_column='DatePosted', blank=True, null=True)  # Field name made lowercase.
    market = models.TextField(db_column='Market', blank=True, null=True)  # Field name made lowercase.
    shipmethodid = models.IntegerField(db_column='ShipMethodID', blank=True, null=True)  # Field name made lowercase.
    order_type = models.TextField(db_column='Order Type')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    orderlinkid = models.IntegerField(db_column='OrderLinkID', blank=True, null=True)  # Field name made lowercase.
    autoshipscheduleid = models.IntegerField(db_column='AutoShipScheduleID', blank=True, null=True)  # Field name made lowercase.
    autoshipbatchid = models.IntegerField(db_column='AutoshipBatchID', blank=True, null=True)  # Field name made lowercase.
    invoicenotes = models.CharField(db_column='InvoiceNotes', max_length=500, blank=True, null=True)  # Field name made lowercase.
    geocode = models.CharField(db_column='GeoCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_orders'


class BiOrderstatuses(models.Model):
    orderstatusid = models.IntegerField(db_column='OrderStatusID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=25)  # Field name made lowercase.
    official = models.SmallIntegerField(db_column='Official')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_orderstatuses'


class BiPayments(models.Model):
    paymentid = models.IntegerField(db_column='PaymentID')  # Field name made lowercase.
    paymenttypeid = models.IntegerField(db_column='PaymentTypeID')  # Field name made lowercase.
    paymentdate = models.DateTimeField(db_column='PaymentDate')  # Field name made lowercase.
    orderid = models.IntegerField(db_column='OrderID', blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    paymentstatustypeid = models.SmallIntegerField(db_column='PaymentStatusTypeID')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_payments'


class BiPaymentstatustypes(models.Model):
    paymentstatustypeid = models.SmallIntegerField(db_column='PaymentStatusTypeID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    official = models.SmallIntegerField(db_column='Official')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_paymentstatustypes'


class BiPaymenttypes(models.Model):
    paymenttypeid = models.IntegerField(db_column='PaymentTypeID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=25)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    autoship = models.SmallIntegerField(db_column='Autoship', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_paymenttypes'


class BiPayoutdetails(models.Model):
    payoutdetailid = models.IntegerField(db_column='PayoutDetailID')  # Field name made lowercase.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    payoutprocessid = models.IntegerField(db_column='PayoutProcessID')  # Field name made lowercase.
    prevbalanceforward = models.DecimalField(db_column='PrevBalanceForward', max_digits=19, decimal_places=4)  # Field name made lowercase.
    adjustments = models.DecimalField(db_column='Adjustments', max_digits=19, decimal_places=4)  # Field name made lowercase.
    bonusamount = models.DecimalField(db_column='BonusAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    preconversionamount = models.DecimalField(db_column='PreConversionAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    postconversionamount = models.DecimalField(db_column='PostConversionAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    balanceforward = models.DecimalField(db_column='BalanceForward', max_digits=19, decimal_places=4)  # Field name made lowercase.
    payoutfee = models.DecimalField(db_column='PayoutFee', max_digits=19, decimal_places=4)  # Field name made lowercase.
    reference_field = models.IntegerField(db_column='Reference #')  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    preconversioncurrencyid = models.IntegerField(db_column='PreConversionCurrencyID')  # Field name made lowercase.
    postconversioncurrencyid = models.IntegerField(db_column='PostConversionCurrencyID')  # Field name made lowercase.
    payoutmethodid = models.IntegerField(db_column='PayoutMethodID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_payoutdetails'


class BiPayoutmethods(models.Model):
    payoutmethodid = models.IntegerField(db_column='PayoutMethodID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    nextreferencenumber = models.IntegerField(db_column='NextReferenceNumber')  # Field name made lowercase.
    active = models.SmallIntegerField(db_column='Active')  # Field name made lowercase.
    minpayoutamount = models.DecimalField(db_column='MinPayoutAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    processingfee = models.DecimalField(db_column='ProcessingFee', max_digits=19, decimal_places=4)  # Field name made lowercase.
    payoutmethodtype = models.CharField(db_column='PayoutMethodType', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_payoutmethods'


class BiPayoutprocesses(models.Model):
    payoutprocessid = models.IntegerField(db_column='PayoutProcessID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, blank=True, null=True)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_payoutprocesses'


class BiQualificationagentdetails(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    qualificationagentid = models.IntegerField(db_column='QualificationAgentID')  # Field name made lowercase.
    compqualprocessorcriteriaid = models.IntegerField(db_column='CompQualProcessorCriteriaID')  # Field name made lowercase.
    value = models.TextField(db_column='Value', blank=True, null=True)  # Field name made lowercase.
    criteriacompqualagentid = models.IntegerField(db_column='CriteriaCompQualAgentID', blank=True, null=True)  # Field name made lowercase.
    compoperatorid = models.SmallIntegerField(db_column='CompOperatorID', blank=True, null=True)  # Field name made lowercase.
    compositelevel = models.SmallIntegerField(db_column='CompositeLevel')  # Field name made lowercase.
    isoroperator = models.SmallIntegerField(db_column='IsOrOperator')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_qualificationagentdetails'


class BiQualificationagents(models.Model):
    qualificationagentid = models.IntegerField(db_column='QualificationAgentID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)  # Field name made lowercase.
    configuration = models.CharField(db_column='Configuration', max_length=100, blank=True, null=True)  # Field name made lowercase.
    qualificationagent_groupid = models.IntegerField(db_column='QualificationAgent_GroupID', blank=True, null=True)  # Field name made lowercase.
    bonus_parameter = models.TextField(db_column='Bonus Parameter')  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'bi_qualificationagents'


class BiQualificationagentvalues(models.Model):
    qualificationagentid = models.IntegerField(db_column='QualificationAgentID')  # Field name made lowercase.
    bonusrepid = models.BigIntegerField(db_column='BonusRepID')  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_qualificationagentvalues'


class BiRankpricetypes(models.Model):
    rankpricetypeid = models.IntegerField(db_column='RankPriceTypeID')  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=25)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_rankpricetypes'


class BiRanks(models.Model):
    rankid = models.IntegerField(db_column='RankID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)  # Field name made lowercase.
    active = models.SmallIntegerField(db_column='Active')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_ranks'


class BiRepbonusdata(models.Model):
    bonusrepid = models.BigIntegerField(db_column='BonusRepID')  # Field name made lowercase.
    bonusrunid = models.IntegerField(db_column='BonusRunID')  # Field name made lowercase.
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    titlerankid = models.SmallIntegerField(db_column='TitleRankID')  # Field name made lowercase.
    bonusrankid = models.IntegerField(db_column='BonusRankID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_repbonusdata'


class BiReps(models.Model):
    repid = models.IntegerField(db_column='RepID')  # Field name made lowercase.
    rep_field = models.CharField(db_column='Rep #', max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    enrollerrepid = models.IntegerField(db_column='EnrollerRepID', blank=True, null=True)  # Field name made lowercase.
    uplinebcid = models.IntegerField(db_column='UplineBCID', blank=True, null=True)  # Field name made lowercase.
    bcposition = models.TextField(db_column='BCPosition', blank=True, null=True)  # Field name made lowercase.
    bcid = models.IntegerField(db_column='BCID')  # Field name made lowercase.
    bc_field = models.IntegerField(db_column='BC #', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    firstname = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    middleinitial = models.CharField(db_column='MiddleInitial', max_length=1, blank=True, null=True)  # Field name made lowercase.
    joindate = models.DateTimeField(db_column='JoinDate')  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstreet1 = models.CharField(db_column='BillStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstreet2 = models.CharField(db_column='BillStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcity = models.CharField(db_column='BillCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcounty = models.CharField(db_column='BillCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billstate = models.CharField(db_column='BillState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billpostalcode = models.CharField(db_column='BillPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    billcountry = models.CharField(db_column='BillCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dateofbirth = models.DateTimeField(db_column='DateOfBirth', blank=True, null=True)  # Field name made lowercase.
    renewaldate = models.DateTimeField(db_column='RenewalDate')  # Field name made lowercase.
    payoutmethodid = models.IntegerField(db_column='PayoutMethodID', blank=True, null=True)  # Field name made lowercase.
    reptypeid = models.IntegerField(db_column='RepTypeID')  # Field name made lowercase.
    rankid = models.IntegerField(db_column='RankID')  # Field name made lowercase.
    date_cancelled = models.DateTimeField(db_column='Date Cancelled', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    taxid1 = models.CharField(db_column='TaxID1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    taxid2 = models.CharField(db_column='TaxID2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    taxexempt = models.SmallIntegerField(db_column='TaxExempt', blank=True, null=True)  # Field name made lowercase.
    phone1 = models.CharField(db_column='Phone1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone2 = models.CharField(db_column='Phone2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone3 = models.CharField(db_column='Phone3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone4 = models.CharField(db_column='Phone4', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone5 = models.CharField(db_column='Phone5', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone6 = models.CharField(db_column='Phone6', max_length=50, blank=True, null=True)  # Field name made lowercase.
    preferredculture = models.IntegerField(db_column='PreferredCulture')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_reps'


class BiReptypes(models.Model):
    reptypeid = models.IntegerField(db_column='RepTypeID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_reptypes'


class BiShipmethods(models.Model):
    shipmethodid = models.IntegerField(db_column='ShipMethodID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)  # Field name made lowercase.
    shipper = models.CharField(db_column='Shipper', max_length=50)  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=100, blank=True, null=True)  # Field name made lowercase.
    trackingurl = models.CharField(db_column='TrackingURL', max_length=250, blank=True, null=True)  # Field name made lowercase.
    active = models.SmallIntegerField(db_column='Active')  # Field name made lowercase.
    multipleunit = models.CharField(db_column='MultipleUnit', max_length=50, blank=True, null=True)  # Field name made lowercase.
    web = models.SmallIntegerField(db_column='Web', blank=True, null=True)  # Field name made lowercase.
    priority = models.IntegerField(db_column='Priority')  # Field name made lowercase.
    immediate = models.SmallIntegerField(db_column='Immediate', blank=True, null=True)  # Field name made lowercase.
    surchargepercentage = models.DecimalField(db_column='SurchargePercentage', max_digits=18, decimal_places=8)  # Field name made lowercase.
    handlingfeeaware = models.SmallIntegerField(db_column='HandlingFeeAware')  # Field name made lowercase.
    surchargebase = models.DecimalField(db_column='SurchargeBase', max_digits=19, decimal_places=4)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_shipmethods'


class BiTaxcodes(models.Model):
    taxcodeid = models.CharField(db_column='TaxCodeID', max_length=25)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, blank=True, null=True)  # Field name made lowercase.
    visibleonextranet = models.SmallIntegerField(db_column='VisibleOnExtranet', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_taxcodes'


class BiWarehouses(models.Model):
    warehouseid = models.IntegerField(db_column='WarehouseID')  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.
    packslipline1 = models.CharField(db_column='PackSlipLine1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    packslipline2 = models.CharField(db_column='PackSlipLine2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    packslipline3 = models.CharField(db_column='PackSlipLine3', max_length=100, blank=True, null=True)  # Field name made lowercase.
    packslipline4 = models.CharField(db_column='PackSlipLine4', max_length=100, blank=True, null=True)  # Field name made lowercase.
    packslipline5 = models.CharField(db_column='PackSlipLine5', max_length=100, blank=True, null=True)  # Field name made lowercase.
    packslipline6 = models.CharField(db_column='PackSlipLine6', max_length=100, blank=True, null=True)  # Field name made lowercase.
    active = models.SmallIntegerField(db_column='Active')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bi_warehouses'


class MssubscriptionAgents(models.Model):
    id = models.IntegerField()
    publisher = models.CharField(max_length=128)
    publisher_db = models.CharField(max_length=128)
    publication = models.CharField(max_length=128)
    subscription_type = models.IntegerField()
    queue_id = models.CharField(max_length=128, blank=True, null=True)
    update_mode = models.SmallIntegerField()
    failover_mode = models.NullBooleanField()
    spid = models.IntegerField()
    login_time = models.DateTimeField()
    allow_subscription_copy = models.NullBooleanField()
    attach_state = models.IntegerField()
    attach_version = models.BinaryField()
    last_sync_status = models.IntegerField(blank=True, null=True)
    last_sync_summary = models.CharField(max_length=128, blank=True, null=True)
    last_sync_time = models.DateTimeField(blank=True, null=True)
    queue_server = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mssubscription_agents'
