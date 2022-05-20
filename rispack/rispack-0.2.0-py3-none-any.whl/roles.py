from enum import Enum, unique


@unique
class AdminRole(Enum):
    SERVICING_VIEW = "servicing.view"
    PROFILE_CREATION = "profile.creation"
    PROFILE_APPROVAL = "profile.approve"
    LOAN_VIEW = "loan.view"
    LOAN_APPROVAL = "loan.approval"
    VIP_CREATION = "vip.creation"
    WITHDRAW_VIEW = "withdraw.view"
    WITHDRAW_APPROVAL = "withdraw.approval"
    PARTNER_CREATION = "partner.creation"
    WALLET_VIEW = "wallet.view"
    USER_CREATION = "user.creation"
    USER_REMOVAL = "user.removal"
    QUOTE_CREATION = "quote.creation"
