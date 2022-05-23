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

import sys

from django.db import models


# the database is only created during tests
IS_MANAGED = 'testing' not in sys.argv


class BiAutoship(models.Model):
    rep_field = models.CharField(db_column='Rep #', max_length=20, blank=True, null=True)
    repid = models.IntegerField(db_column='RepID')
    customerid = models.IntegerField(db_column='CustomerID')
    bcid = models.IntegerField(db_column='BCID')
    autoshipscheduleid = models.IntegerField(db_column='AutoshipScheduleID')
    autoshipperiodtypeid = models.IntegerField(db_column='AutoshipPeriodTypeID')
    period_unit = models.IntegerField(db_column='Period Unit')
    startdate = models.DateTimeField(db_column='StartDate')
    stopdate = models.DateTimeField(db_column='StopDate')
    datenextrun = models.DateTimeField(db_column='DateNextRun')
    autoshipruleid = models.IntegerField(db_column='AutoshipRuleID', blank=True, null=True)
    shipmethodid = models.IntegerField(db_column='ShipMethodID', blank=True, null=True)
    shipname1 = models.CharField(db_column='ShipName1', max_length=50, blank=True, null=True)
    shipname2 = models.CharField(db_column='ShipName2', max_length=50, blank=True, null=True)
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)
    shipphone = models.CharField(db_column='ShipPhone', max_length=50, blank=True, null=True)
    creditcardprofileid = models.IntegerField(db_column='CreditCardProfileID', blank=True, null=True)
    achprofileid = models.IntegerField(db_column='ACHProfileID', blank=True, null=True)
    checkdraftprofileid = models.IntegerField(db_column='CheckDraftProfileID', blank=True, null=True)
    orderid = models.IntegerField(db_column='OrderID', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_autoship'


class BiAutoshipdetails(models.Model):
    autoshipscheduleid = models.IntegerField(db_column='AutoshipScheduleID')
    autoshipdetailid = models.IntegerField(db_column='AutoShipDetailID')
    inventoryid = models.IntegerField(db_column='InventoryID')
    groupitem = models.SmallIntegerField(db_column='GroupItem', blank=True, null=True)
    quantity = models.IntegerField(db_column='Quantity')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_autoshipdetails'


class BiAutoshipperiodtypes(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=25, blank=True, null=True)
    explanation = models.CharField(db_column='Explanation', max_length=150, blank=True, null=True)
    repextdescription = models.CharField(db_column='RepExtDescription', max_length=100, blank=True, null=True)
    custextdescription = models.CharField(db_column='CustExtDescription', max_length=100, blank=True, null=True)
    datepart = models.TextField(db_column='DatePart')
    increment = models.SmallIntegerField(db_column='Increment')
    useperiodday = models.SmallIntegerField(db_column='UsePeriodDay')
    isactive = models.SmallIntegerField(db_column='IsActive')
    isallowextranetedit = models.SmallIntegerField(db_column='IsAllowExtranetEdit')
    isrepextallowselection = models.SmallIntegerField(db_column='IsRepExtAllowSelection')
    iscustextallowselection = models.SmallIntegerField(db_column='IsCustExtAllowSelection')
    isallowexteditpayments = models.SmallIntegerField(db_column='IsAllowExtEditPayments', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_autoshipperiodtypes'


class BiBonusagentgroups(models.Model):
    id = models.IntegerField(db_column='BonusGroupID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_bonusagentgroups'


class BiBonusagents(models.Model):
    id = models.IntegerField(db_column='BonusAgentID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)
    configurationid = models.IntegerField(db_column='ConfigurationID')
    bonusagentgroupid = models.IntegerField(db_column='BonusAgentGroupID', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_bonusagents'


class BiBonusdetails(models.Model):
    id = models.IntegerField(primary_key=True, db_column='BonusDetailID')
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4)
    rep = models.ForeignKey(
        "BiRep", db_column='RepID', on_delete=models.DO_NOTHING)
    payon_rep = models.ForeignKey(
        "BiRep", db_column='PayOnRepID', max_length=20, blank=True, null=True,
        related_name="payon_bonus_details", on_delete=models.DO_NOTHING)
    bonusrun = models.ForeignKey("BiBonusRun", db_column='BonusRunID', on_delete=models.DO_NOTHING)
    bonustype = models.ForeignKey("BiBonustypes", db_column='BonusTypeID', on_delete=models.DO_NOTHING)
    orderid = models.IntegerField(db_column='OrderID')
    bonustypereportingvalue1 = models.DecimalField(db_column='BonusTypeReportingValue1', max_digits=18, decimal_places=6)
    bonustypereportingvalue2 = models.DecimalField(db_column='BonusTypeReportingValue2', max_digits=18, decimal_places=6)
    bonustypereportingvalue3 = models.DecimalField(db_column='BonusTypeReportingValue3', max_digits=18, decimal_places=6)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_bonusdetails'


class BiBonusRun(models.Model):
    id = models.IntegerField(primary_key=True, db_column='BonusRunID')
    bonus_description = models.CharField(db_column='Bonus Description', max_length=50, blank=True, null=True)
    period_start = models.DateTimeField(db_column='PeriodStartDate')
    period_end = models.DateTimeField(db_column='PeriodEndDate')
    qualify_start = models.DateTimeField(db_column='QualifyStartDate', blank=True, null=True)
    qualify_end = models.DateTimeField(db_column='QualifyEndDate', blank=True, null=True)
    payoutprocessid = models.IntegerField(db_column='PayoutProcessID')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_bonusruns'


class BiBonustypes(models.Model):
    id = models.IntegerField(primary_key=True, db_column='BonusAgentID')
    description = models.CharField(db_column='Description', max_length=50)
    periodcalendar = models.CharField(db_column='PeriodCalendar', max_length=200, blank=True, null=True)
    isactive = models.IntegerField(db_column='IsActive')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_bonustypes'


class BiCompMatrixData(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    compentityid = models.IntegerField(db_column='CompEntityID')  # Field name made lowercase.
    compentitytypeid = models.IntegerField(db_column='CompEntityTypeID')  # Field name made lowercase.
    dependentcomprankid = models.IntegerField(db_column='DependentCompRankID', blank=True, null=True)  # Field name made lowercase.
    agent = models.ForeignKey(BiBonusagents, db_column='DependentCompQualAgentID', blank=True, null=True, on_delete=models.DO_NOTHING)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    generation = models.IntegerField(db_column='Generation', blank=True, null=True)  # Field name made lowercase.
    minamount = models.DecimalField(db_column='MinAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    maxamount = models.DecimalField(db_column='MaxAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    value1 = models.DecimalField(db_column='Value1', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    value2 = models.DecimalField(db_column='Value2', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=100)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='DateCreated')  # Field name made lowercase.

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_compmatrixdata'


class BiCurrencies(models.Model):
    currencyid = models.IntegerField(db_column='CurrencyID')
    description = models.CharField(db_column='Description', max_length=50)
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10)
    active = models.SmallIntegerField(db_column='Active')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_currencies'


class BiCustomers(models.Model):
    customerid = models.IntegerField(db_column='CustomerID', primary_key=True)
    customer_field = models.CharField(db_column='Customer #', max_length=20, blank=True, null=True)
    repid = models.IntegerField(db_column='RepID')
    firstname = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)
    lastname = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)
    middleinitial = models.CharField(db_column='MiddleInitial', max_length=1, blank=True, null=True)
    joindate = models.DateTimeField(db_column='JoinDate')
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)
    billstreet1 = models.CharField(db_column='BillStreet1', max_length=50, blank=True, null=True)
    billstreet2 = models.CharField(db_column='BillStreet2', max_length=50, blank=True, null=True)
    billcity = models.CharField(db_column='BillCity', max_length=50, blank=True, null=True)
    billcounty = models.CharField(db_column='BillCounty', max_length=50, blank=True, null=True)
    billstate = models.CharField(db_column='BillState', max_length=50, blank=True, null=True)
    billpostalcode = models.CharField(db_column='BillPostalCode', max_length=50, blank=True, null=True)
    billcountry = models.CharField(db_column='BillCountry', max_length=50, blank=True, null=True)
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)
    dateofbirth = models.DateTimeField(db_column='DateOfBirth', blank=True, null=True)
    customertypeid = models.IntegerField(db_column='CustomerTypeID')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_customers'

    def __unicode__(self):
        return u'{} {}'.format(self.firstname, self.lastname)


class BiCustomertypes(models.Model):
    customertypeid = models.IntegerField(db_column='CustomerTypeID')
    description = models.CharField(db_column='Description', max_length=50)
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_customertypes'


class BiInventory(models.Model):
    id = models.IntegerField(db_column='InventoryID', primary_key=True)
    item_field = models.CharField(db_column='Item #', max_length=20)
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)
    explanation = models.CharField(db_column='Explanation', max_length=1000, blank=True, null=True)
    taxcode = models.CharField(db_column='TaxCode', max_length=25)
    isactive = models.SmallIntegerField(db_column='IsActive')
    currencyid = models.IntegerField(db_column='CurrencyID')
    category = models.CharField(db_column='Category', max_length=100)
    cost = models.DecimalField(db_column='Cost', max_digits=19, decimal_places=4, blank=True, null=True)
    featureditemreps = models.SmallIntegerField(db_column='FeaturedItemReps')
    featureditemcustomers = models.SmallIntegerField(db_column='FeaturedItemCustomers')
    outofstocklevel = models.IntegerField(db_column='OutOfStockLevel')
    outofstockmessage = models.CharField(db_column='OutOfStockMessage', max_length=1000, blank=True, null=True)
    lowstocklevel = models.IntegerField(db_column='LowStockLevel')
    lowstockmessage = models.CharField(db_column='LowStockMessage', max_length=1000, blank=True, null=True)
    sortorder = models.IntegerField(db_column='SortOrder')
    virtualitem = models.IntegerField(db_column='VirtualItem')
    freeshipping = models.SmallIntegerField(db_column='FreeShipping')
    shippingsurcharge = models.DecimalField(db_column='ShippingSurcharge', max_digits=19, decimal_places=4)
    shippingsurchargebase = models.DecimalField(db_column='ShippingSurchargeBase', max_digits=19, decimal_places=4)
    weight = models.DecimalField(db_column='Weight', max_digits=10, decimal_places=4, blank=True, null=True)
    groupitemoverrideweight = models.DecimalField(db_column='GroupItemOverrideWeight', max_digits=18, decimal_places=2, blank=True, null=True)
    handlingfee = models.DecimalField(db_column='HandlingFee', max_digits=19, decimal_places=4, blank=True, null=True)
    datecreated = models.DateTimeField(db_column='DateCreated')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_inventory'


class BiInventorycategory(models.Model):
    categoryid = models.IntegerField(db_column='CategoryID')
    category = models.CharField(db_column='Category', max_length=100)
    subcategory = models.CharField(db_column='SubCategory', max_length=100, blank=True, null=True)
    sortorder = models.IntegerField(db_column='SortOrder')
    datecreated = models.DateTimeField(db_column='DateCreated')
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)
    lastmodifiedby = models.CharField(db_column='LastModifiedBy', max_length=100, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_inventorycategory'


class BiInventorycountry(models.Model):
    inventoryid = models.IntegerField(db_column='InventoryID')
    country = models.CharField(db_column='Country', max_length=100, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_inventorycountry'


class BiInventorygroups(models.Model):
    groupid = models.IntegerField(db_column='GroupID')
    parentinventoryid = models.IntegerField(db_column='ParentInventoryID')
    childinventoryid = models.IntegerField(db_column='ChildInventoryID')
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_inventorygroups'


class BiInventoryPrice(models.Model):
    id = models.IntegerField(db_column='PriceID', primary_key=True)
    inventory = models.ForeignKey(BiInventory, db_column='InventoryID', on_delete=models.DO_NOTHING)
    ranktype = models.ForeignKey("BiRank", db_column='RanktypeID', on_delete=models.DO_NOTHING)
    pricetext = models.CharField(db_column='PriceText', max_length=25)
    currencyid = models.IntegerField(db_column='CurrencyID')
    price = models.DecimalField(db_column='Price', max_digits=19, decimal_places=4)
    volume1 = models.DecimalField(db_column='Volume1', max_digits=19, decimal_places=4)
    volume2 = models.DecimalField(db_column='Volume2', max_digits=19, decimal_places=4)
    volume3 = models.DecimalField(db_column='Volume3', max_digits=19, decimal_places=4)
    volume4 = models.DecimalField(db_column='Volume4', max_digits=19, decimal_places=4)
    otherprice1 = models.DecimalField(db_column='OtherPrice1', max_digits=19, decimal_places=4)
    otherprice2 = models.DecimalField(db_column='OtherPrice2', max_digits=19, decimal_places=4)
    otherprice3 = models.DecimalField(db_column='OtherPrice3', max_digits=19, decimal_places=4)
    otherprice4 = models.DecimalField(db_column='OtherPrice4', max_digits=19, decimal_places=4)
    compare = models.DecimalField(db_column='Compare', max_digits=19, decimal_places=4)
    taxableamount = models.DecimalField(db_column='TaxableAmount', max_digits=19, decimal_places=4)
    startdate = models.DateTimeField(db_column='StartDate')
    enddate = models.DateTimeField(db_column='EndDate')
    datecreated = models.DateTimeField(db_column='DateCreated')
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)
    lastmodifiedby = models.CharField(db_column='LastModifiedBy', max_length=100, blank=True, null=True)
    returnprice = models.DecimalField(db_column='ReturnPrice', max_digits=19, decimal_places=4, blank=True, null=True)
    mup_qtystart = models.IntegerField(db_column='MUP_QtyStart')
    mup_qtystop = models.IntegerField(db_column='MUP_QtyStop')
    mup_qtyvalue = models.IntegerField(db_column='MUP_QtyValue')
    shippingvalue = models.DecimalField(db_column='ShippingValue', max_digits=19, decimal_places=4, blank=True, null=True)
    vattax = models.DecimalField(db_column='VATTax', max_digits=19, decimal_places=4)
    handlingfee = models.DecimalField(db_column='HandlingFee', max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_inventoryprices'


class BiInventorywarehouse(models.Model):
    inventory = models.OneToOneField("BiInventory", db_column='InventoryID', primary_key=True, on_delete=models.DO_NOTHING)
    warehouse = models.OneToOneField("BiWarehouses", db_column='WarehouseID', on_delete=models.DO_NOTHING)
    onhand = models.IntegerField(db_column='OnHand')
    reorderpoint = models.IntegerField(db_column='ReOrderPoint', blank=True, null=True)
    onhandshipped = models.IntegerField(db_column='OnHandShipped')
    cost = models.DecimalField(db_column='Cost', max_digits=19, decimal_places=4)
    idealonhand = models.IntegerField(db_column='IdealOnHand')
    avgweightedcost = models.DecimalField(db_column='AvgWeightedCost', max_digits=19, decimal_places=4)
    packslipsortorder = models.IntegerField(db_column='PackSlipSortOrder')
    outofstocklevel = models.IntegerField(db_column='OutOfStockLevel')
    outofstockmessage = models.CharField(db_column='OutOfStockMessage', max_length=300, blank=True, null=True)
    lowstocklevel = models.IntegerField(db_column='LowStockLevel')
    lowstockmessage = models.CharField(db_column='LowStockMessage', max_length=300, blank=True, null=True)
    packslipproductid = models.CharField(db_column='PackslipProductID', max_length=40, blank=True, null=True)
    packslipdescription = models.CharField(db_column='PackslipDescription', max_length=200, blank=True, null=True)
    softcount = models.IntegerField(db_column='SoftCount')
    datecreated = models.DateTimeField(db_column='DateCreated')
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)
    datelastmodified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)
    lastmodifiedby = models.CharField(db_column='LastModifiedBy', max_length=100, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_inventorywarehouse'


class BiOrderdetails(models.Model):
    order = models.ForeignKey("BiOrders", related_name="items", db_column='OrderID', on_delete=models.DO_NOTHING)
    id = models.IntegerField(db_column='OrderDetailID', primary_key=True)
    orderdetailstatusid = models.IntegerField(db_column='OrderDetailStatusID')
    inventory = models.ForeignKey("BiInventory", db_column='InventoryID', on_delete=models.DO_NOTHING)
    groupitem = models.IntegerField(db_column='GroupItem')
    groupownerdetailid = models.IntegerField(db_column='GroupOwnerDetailID')
    packslipped = models.IntegerField(db_column='PackSlipped')
    quantity = models.IntegerField(db_column='Quantity')
    volume1 = models.DecimalField(db_column='Volume1', max_digits=19, decimal_places=4)
    volume2 = models.DecimalField(db_column='Volume2', max_digits=19, decimal_places=4)
    volume3 = models.DecimalField(db_column='Volume3', max_digits=19, decimal_places=4)
    volume4 = models.DecimalField(db_column='Volume4', max_digits=19, decimal_places=4)
    otherprice1 = models.DecimalField(db_column='OtherPrice1', max_digits=19, decimal_places=4)
    otherprice2 = models.DecimalField(db_column='OtherPrice2', max_digits=19, decimal_places=4)
    otherprice3 = models.DecimalField(db_column='OtherPrice3', max_digits=19, decimal_places=4)
    otherprice4 = models.DecimalField(db_column='OtherPrice4', max_digits=19, decimal_places=4)
    price = models.DecimalField(db_column='Price', max_digits=19, decimal_places=4)
    tax = models.DecimalField(db_column='Tax', max_digits=19, decimal_places=4, blank=True, null=True)
    taxableamount = models.DecimalField(db_column='TaxableAmount', max_digits=19, decimal_places=4)
    compare = models.DecimalField(db_column='Compare', max_digits=19, decimal_places=4)
    trackingid = models.CharField(db_column='TrackingID', max_length=50, blank=True, null=True)
    warehouseid = models.IntegerField(db_column='WarehouseID', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_orderdetails'


class BiOrderdetailstatuses(models.Model):
    orderdetailstatusid = models.IntegerField(db_column='OrderDetailStatusID')
    description = models.CharField(db_column='Description', max_length=50)
    official = models.SmallIntegerField(db_column='Official')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_orderdetailstatuses'


class BiOrders(models.Model):
    id = models.IntegerField(db_column='OrderID', primary_key=True)
    rep = models.ForeignKey("BiRep", db_column='RepID', on_delete=models.DO_NOTHING)
    bcid = models.IntegerField(db_column='BCID')
    customer = models.ForeignKey("BiCustomers", db_column='CustomerID', blank=True, null=True, on_delete=models.DO_NOTHING)
    partyid = models.IntegerField(db_column='PartyID', blank=True, null=True)
    orderdate = models.DateTimeField(db_column='OrderDate')
    bonusdate = models.DateTimeField(db_column='BonusDate')
    dateshipped = models.DateTimeField(db_column='DateShipped', blank=True, null=True)
    status = models.ForeignKey("BiOrderstatuses", db_column='OrderStatusID', on_delete=models.DO_NOTHING)
    rankpricetypeid = models.IntegerField(db_column='RankPriceTypeID')
    shipping = models.DecimalField(db_column='Shipping', max_digits=19, decimal_places=4)
    handling = models.DecimalField(db_column='Handling', max_digits=19, decimal_places=4)
    shippingtax = models.DecimalField(db_column='ShippingTax', max_digits=19, decimal_places=4)
    handlingtax = models.DecimalField(db_column='HandlingTax', max_digits=19, decimal_places=4)
    totalprice = models.DecimalField(db_column='TotalPrice', max_digits=19, decimal_places=4)
    currencytypeid = models.IntegerField(db_column='CurrencyTypeID', blank=True, null=True)
    billstreet1 = models.CharField(db_column='BillStreet1', max_length=50, blank=True, null=True)
    billstreet2 = models.CharField(db_column='BillStreet2', max_length=50, blank=True, null=True)
    billcity = models.CharField(db_column='BillCity', max_length=50, blank=True, null=True)
    billcounty = models.CharField(db_column='BillCounty', max_length=50, blank=True, null=True)
    billstate = models.CharField(db_column='BillState', max_length=50, blank=True, null=True)
    billpostalcode = models.CharField(db_column='BillPostalCode', max_length=50, blank=True, null=True)
    billcountry = models.CharField(db_column='BillCountry', max_length=50, blank=True, null=True)
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)
    dateposted = models.DateTimeField(db_column='DatePosted', blank=True, null=True)
    market = models.TextField(db_column='Market', blank=True, null=True)
    shipmethod = models.ForeignKey("BiShipmethods", db_column='ShipMethodID', blank=True, null=True, on_delete=models.DO_NOTHING)
    order_type = models.TextField(db_column='Order Type')
    orderlinkid = models.IntegerField(db_column='OrderLinkID', blank=True, null=True)
    autoshipscheduleid = models.IntegerField(db_column='AutoShipScheduleID', blank=True, null=True)
    autoshipbatchid = models.IntegerField(db_column='AutoshipBatchID', blank=True, null=True)
    invoicenotes = models.CharField(db_column='InvoiceNotes', max_length=500, blank=True, null=True)
    geocode = models.CharField(db_column='GeoCode', max_length=10, blank=True, null=True)
    created = models.DateTimeField(db_column='DateCreated')
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_orders'


class BiOrderstatuses(models.Model):
    id = models.IntegerField(db_column='OrderStatusID',primary_key=True)
    description = models.CharField(db_column='Description', max_length=25)
    official = models.SmallIntegerField(db_column='Official')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_orderstatuses'


class BiPayments(models.Model):
    id = models.IntegerField(primary_key=True, db_column='PaymentID')
    paymenttype = models.ForeignKey("BiPaymenttypes", db_column='PaymentTypeID', on_delete=models.DO_NOTHING)
    paymentdate = models.DateTimeField(db_column='PaymentDate')
    orderid = models.IntegerField(db_column='OrderID', blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4)
    paymentstatustypeid = models.SmallIntegerField(db_column='PaymentStatusTypeID')
    datecreated = models.DateTimeField(db_column='DateCreated')
    createdby = models.CharField(db_column='CreatedBy', max_length=100, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_payments'


class BiPaymentstatustypes(models.Model):
    paymentstatustypeid = models.SmallIntegerField(db_column='PaymentStatusTypeID')
    description = models.CharField(db_column='Description', max_length=50)
    official = models.SmallIntegerField(db_column='Official')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_paymentstatustypes'


class BiPaymenttypes(models.Model):
    paymenttypeid = models.IntegerField(primary_key=True, db_column='PaymentTypeID')
    description = models.CharField(db_column='Description', max_length=25)
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)
    autoship = models.SmallIntegerField(db_column='Autoship', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_paymenttypes'


class BiPayoutdetails(models.Model):
    payoutdetailid = models.IntegerField(db_column='PayoutDetailID')
    repid = models.IntegerField(db_column='RepID')
    payoutprocessid = models.IntegerField(db_column='PayoutProcessID')
    prevbalanceforward = models.DecimalField(db_column='PrevBalanceForward', max_digits=19, decimal_places=4)
    adjustments = models.DecimalField(db_column='Adjustments', max_digits=19, decimal_places=4)
    bonusamount = models.DecimalField(db_column='BonusAmount', max_digits=19, decimal_places=4)
    preconversionamount = models.DecimalField(db_column='PreConversionAmount', max_digits=19, decimal_places=4)
    postconversionamount = models.DecimalField(db_column='PostConversionAmount', max_digits=19, decimal_places=4)
    balanceforward = models.DecimalField(db_column='BalanceForward', max_digits=19, decimal_places=4)
    payoutfee = models.DecimalField(db_column='PayoutFee', max_digits=19, decimal_places=4)
    reference_field = models.IntegerField(db_column='Reference #')
    datecreated = models.DateTimeField(db_column='DateCreated')
    preconversioncurrencyid = models.IntegerField(db_column='PreConversionCurrencyID')
    postconversioncurrencyid = models.IntegerField(db_column='PostConversionCurrencyID')
    payoutmethodid = models.IntegerField(db_column='PayoutMethodID')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_payoutdetails'


class BiPayoutmethods(models.Model):
    payoutmethodid = models.IntegerField(db_column='PayoutMethodID')
    description = models.CharField(db_column='Description', max_length=50)
    nextreferencenumber = models.IntegerField(db_column='NextReferenceNumber')
    active = models.SmallIntegerField(db_column='Active')
    minpayoutamount = models.DecimalField(db_column='MinPayoutAmount', max_digits=19, decimal_places=4)
    processingfee = models.DecimalField(db_column='ProcessingFee', max_digits=19, decimal_places=4)
    payoutmethodtype = models.CharField(db_column='PayoutMethodType', max_length=50)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_payoutmethods'


class BiPayoutprocesses(models.Model):
    payoutprocessid = models.IntegerField(db_column='PayoutProcessID')
    description = models.CharField(db_column='Description', max_length=250, blank=True, null=True)
    datecreated = models.DateTimeField(db_column='DateCreated')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_payoutprocesses'


class BiQualificationAgent(models.Model):
    id = models.IntegerField(db_column='QualificationAgentID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)
    configuration = models.CharField(db_column='Configuration', max_length=100, blank=True, null=True)
    qualificationagent_groupid = models.IntegerField(db_column='QualificationAgent_GroupID', blank=True, null=True)
    bonus_parameter = models.TextField(db_column='Bonus Parameter')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_qualificationagents'


class BiQualificationAgentValue(models.Model):
    agent = models.OneToOneField(BiQualificationAgent, db_column='QualificationAgentID', primary_key=True, on_delete=models.DO_NOTHING)
    rep_bonus_data = models.OneToOneField("BiRepBonusData", db_column='BonusRepID', on_delete=models.DO_NOTHING)
    value = models.FloatField(db_column='Value', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_qualificationagentvalues'


class BiRankPriceType(models.Model):
    id = models.IntegerField(db_column='RankPriceTypeID', primary_key=True)
    rank = models.ForeignKey("BiRank", db_column='RankID', on_delete=models.DO_NOTHING)
    description = models.CharField(db_column='Description', max_length=25)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_rankpricetypes'


class BiRank(models.Model):
    id = models.IntegerField(db_column='RankID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=50)
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)
    active = models.SmallIntegerField(db_column='Active')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_ranks'

    def __unicode__(self):
        return self.description


class BiRepBonusData(models.Model):
    id = models.BigIntegerField(db_column='BonusRepID', primary_key=True)
    bonusrun = models.ForeignKey("BiBonusRun", db_column='BonusRunID', on_delete=models.DO_NOTHING)
    rep = models.ForeignKey("BiRep", db_column='RepID', on_delete=models.DO_NOTHING)
    title_rank = models.ForeignKey("BiRank", related_name="+", db_column='TitleRankID', on_delete=models.DO_NOTHING)
    bonus_rank = models.ForeignKey("BiRank", db_column='BonusRankID', blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_repbonusdata'


class BiRep(models.Model):
    id = models.IntegerField(db_column='RepID', primary_key=True)
    rep_field = models.CharField(db_column='Rep #', max_length=20)
    enroller = models.ForeignKey("self", db_column='EnrollerRepID', blank=True, null=True, on_delete=models.DO_NOTHING)
    uplinebcid = models.IntegerField(db_column='UplineBCID', blank=True, null=True)
    bcposition = models.TextField(db_column='BCPosition', blank=True, null=True)
    bcid = models.IntegerField(db_column='BCID')
    bc_field = models.IntegerField(db_column='BC #', blank=True, null=True)
    firstname = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)
    lastname = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)
    middleinitial = models.CharField(db_column='MiddleInitial', max_length=1, blank=True, null=True)
    join_date = models.DateTimeField(db_column='JoinDate')
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)
    billstreet1 = models.CharField(db_column='BillStreet1', max_length=50, blank=True, null=True)
    billstreet2 = models.CharField(db_column='BillStreet2', max_length=50, blank=True, null=True)
    billcity = models.CharField(db_column='BillCity', max_length=50, blank=True, null=True)
    billcounty = models.CharField(db_column='BillCounty', max_length=50, blank=True, null=True)
    billstate = models.CharField(db_column='BillState', max_length=50, blank=True, null=True)
    billpostalcode = models.CharField(db_column='BillPostalCode', max_length=50, blank=True, null=True)
    billcountry = models.CharField(db_column='BillCountry', max_length=50, blank=True, null=True)
    shipstreet1 = models.CharField(db_column='ShipStreet1', max_length=50, blank=True, null=True)
    shipstreet2 = models.CharField(db_column='ShipStreet2', max_length=50, blank=True, null=True)
    shipcity = models.CharField(db_column='ShipCity', max_length=50, blank=True, null=True)
    shipcounty = models.CharField(db_column='ShipCounty', max_length=50, blank=True, null=True)
    shipstate = models.CharField(db_column='ShipState', max_length=50, blank=True, null=True)
    shippostalcode = models.CharField(db_column='ShipPostalCode', max_length=50, blank=True, null=True)
    shipcountry = models.CharField(db_column='ShipCountry', max_length=50, blank=True, null=True)
    dateofbirth = models.DateTimeField(db_column='DateOfBirth', blank=True, null=True)
    renewal_date = models.DateTimeField(db_column='RenewalDate')
    payoutmethodid = models.IntegerField(db_column='PayoutMethodID', blank=True, null=True)
    type = models.ForeignKey("BiReptypes", db_column='RepTypeID', on_delete=models.DO_NOTHING)
    rank = models.ForeignKey("BiRank", db_column='RankID', on_delete=models.DO_NOTHING)
    taxid1 = models.CharField(db_column='TaxID1', max_length=50, blank=True, null=True)
    taxid2 = models.CharField(db_column='TaxID2', max_length=50, blank=True, null=True)
    taxexempt = models.SmallIntegerField(db_column='TaxExempt', blank=True, null=True)
    phone1 = models.CharField(db_column='Phone1', max_length=50, blank=True, null=True)
    phone2 = models.CharField(db_column='Phone2', max_length=50, blank=True, null=True)
    phone3 = models.CharField(db_column='Phone3', max_length=50, blank=True, null=True)
    phone4 = models.CharField(db_column='Phone4', max_length=50, blank=True, null=True)
    phone5 = models.CharField(db_column='Phone5', max_length=50, blank=True, null=True)
    phone6 = models.CharField(db_column='Phone6', max_length=50, blank=True, null=True)
    preferredculture = models.IntegerField(db_column='PreferredCulture')
    created = models.DateTimeField(db_column='DateCreated')
    last_modified = models.DateTimeField(db_column='DateLastModified', blank=True, null=True)
    date_cancelled = models.DateTimeField(db_column='Date Cancelled', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_reps'

    def __unicode__(self):
        return u'#{} ({} {})'.format(self.id, self.firstname, self.lastname)


class BiReptypes(models.Model):
    id = models.IntegerField(primary_key=True, db_column='RepTypeID')
    description = models.CharField(db_column='Description', max_length=50)
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_reptypes'

    def __unicode__(self):
        return self.description


class BiShipmethods(models.Model):
    id = models.IntegerField(db_column='ShipMethodID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=50)
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, blank=True, null=True)
    shipper = models.CharField(db_column='Shipper', max_length=50)
    website = models.CharField(db_column='Website', max_length=100, blank=True, null=True)
    trackingurl = models.CharField(db_column='TrackingURL', max_length=250, blank=True, null=True)
    active = models.SmallIntegerField(db_column='Active')
    multipleunit = models.CharField(db_column='MultipleUnit', max_length=50, blank=True, null=True)
    web = models.SmallIntegerField(db_column='Web', blank=True, null=True)
    priority = models.IntegerField(db_column='Priority')
    immediate = models.SmallIntegerField(db_column='Immediate', blank=True, null=True)
    surchargepercentage = models.DecimalField(db_column='SurchargePercentage', max_digits=18, decimal_places=8)
    handlingfeeaware = models.SmallIntegerField(db_column='HandlingFeeAware')
    surchargebase = models.DecimalField(db_column='SurchargeBase', max_digits=19, decimal_places=4)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_shipmethods'


class BiTaxcodes(models.Model):
    id = models.CharField(db_column='TaxCodeID', max_length=25, primary_key=True)
    description = models.CharField(db_column='Description', max_length=250, blank=True, null=True)
    visibleonextranet = models.SmallIntegerField(db_column='VisibleOnExtranet', blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_taxcodes'


class BiWarehouses(models.Model):
    warehouseid = models.IntegerField(db_column='WarehouseID', primary_key=True)
    description = models.CharField(db_column='Description', max_length=50)
    packslipline1 = models.CharField(db_column='PackSlipLine1', max_length=100, blank=True, null=True)
    packslipline2 = models.CharField(db_column='PackSlipLine2', max_length=100, blank=True, null=True)
    packslipline3 = models.CharField(db_column='PackSlipLine3', max_length=100, blank=True, null=True)
    packslipline4 = models.CharField(db_column='PackSlipLine4', max_length=100, blank=True, null=True)
    packslipline5 = models.CharField(db_column='PackSlipLine5', max_length=100, blank=True, null=True)
    packslipline6 = models.CharField(db_column='PackSlipLine6', max_length=100, blank=True, null=True)
    active = models.SmallIntegerField(db_column='Active')

    class Meta:
        managed = IS_MANAGED
        db_table = 'bi_warehouses'


class MssubscriptionAgents(models.Model):
    id = models.IntegerField(primary_key=True)
    publisher = models.CharField(max_length=128)
    publisher_db = models.CharField(max_length=128)
    publication = models.CharField(max_length=128)
    subscription_type = models.IntegerField()
    queue_id = models.CharField(max_length=128, blank=True, null=True)
    update_mode = models.SmallIntegerField()
    failover_mode = models.BooleanField(default=False)
    spid = models.IntegerField()
    login_time = models.DateTimeField()
    allow_subscription_copy = models.BooleanField(default=False)
    attach_state = models.IntegerField()
    attach_version = models.BinaryField()
    last_sync_status = models.IntegerField(blank=True, null=True)
    last_sync_summary = models.CharField(max_length=128, blank=True, null=True)
    last_sync_time = models.DateTimeField(blank=True, null=True)
    queue_server = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = IS_MANAGED
        db_table = 'mssubscription_agents'
