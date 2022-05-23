from django.contrib import admin

from .models import *


# admin.site.register(BiAutoship)
# admin.site.register(BiAutoshipdetails)
# admin.site.register(BiAutoshipperiodtypes)
# admin.site.register(BiBonusagentgroups)
# admin.site.register(BiBonusagents)
# admin.site.register(BiBonusdetails)
# admin.site.register(BiBonusRun)
# admin.site.register(BiBonustypes)
# admin.site.register(BiCompMatrixData)
# admin.site.register(BiCurrencies)
# admin.site.register(BiCustomers)
# admin.site.register(BiCustomertypes)

class BiInventoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'item_field',
        'description',
        'explanation',
        'taxcode',
        'isactive',
        'currencyid',
        'category',
        'cost',
        'featureditemreps',
        'featureditemcustomers',
        'outofstocklevel',
        'outofstockmessage',
        'lowstocklevel',
        'lowstockmessage',
        'sortorder',
        'virtualitem',
        'freeshipping',
        'shippingsurcharge',
        'shippingsurchargebase',
        'weight',
        'groupitemoverrideweight',
        'handlingfee',
        'datecreated',
    ]
admin.site.register(BiInventory, BiInventoryAdmin)

# admin.site.register(BiInventorycategory)
# admin.site.register(BiInventorycountry)
# admin.site.register(BiInventorygroups)
# admin.site.register(BiInventoryprices)
# admin.site.register(BiInventorywarehouse)
# admin.site.register(BiOrderdetails)
# admin.site.register(BiOrderdetailstatuses)
# admin.site.register(BiOrders)
# admin.site.register(BiOrderstatuses)
# admin.site.register(BiPayments)
# admin.site.register(BiPaymentstatustypes)
# admin.site.register(BiPaymenttypes)
# admin.site.register(BiPayoutdetails)
# admin.site.register(BiPayoutmethods)
# admin.site.register(BiPayoutprocesses)
# admin.site.register(BiQualificationAgent)
# admin.site.register(BiQualificationAgentValue)
# admin.site.register(BiRankpricetypes)
# admin.site.register(BiRank)
# admin.site.register(BiRepBonusData)
# admin.site.register(BiRep)
# admin.site.register(BiReptypes)
# admin.site.register(BiShipmethods)
# admin.site.register(BiTaxcodes)
# admin.site.register(BiWarehouses)
# admin.site.register(MssubscriptionAgents)
