import attrs


def hex_converter(value: str | int | None) -> int | None:
    if isinstance(value, int):
        return value
    elif value is None:
        return None
    else:
        return int(value, 16)


@attrs.define(frozen=True)
class _GraphQLMeta:
    json_version: int


@attrs.define(frozen=True)
class OtherCurrencyData:
    currency: int
    value: int = attrs.field(converter=hex_converter)


@attrs.define(frozen=True)
class BlockData:
    pass


@attrs.define(frozen=True)
class AccountData(_GraphQLMeta):
    id: str
    acc_type: int
    acc_type_name: str  # Uninit, Active, Frozen, NonExist
    balance: int = attrs.field(converter=hex_converter)
    bits: int = attrs.field(converter=hex_converter)
    boc: str
    cells: int = attrs.field(converter=hex_converter)
    last_paid: int
    last_trans_lt: int = attrs.field(converter=hex_converter)
    public_cells: int = attrs.field(converter=hex_converter)
    workchain_id: int
    balance_other: list[OtherCurrencyData] = None
    code: str = None
    code_hash: str = None
    data: str = None
    data_hash: str = None
    due_payment: int = attrs.field(converter=hex_converter, default=None)
    init_code_hash: str = None
    library: str = None
    library_hash: str = None
    proof: str = None
    split_depth: int = None
    state_hash: str = None
    tick: bool = None
    tock: bool = None


@attrs.define(frozen=True)
class MessageData(_GraphQLMeta):
    id: str
    boc: str
    dst: str
    msg_type: int
    msg_type_name: str  # Internal, ExtIn, ExtOut
    src: str
    status: int
    status_name: str
    block: BlockData = None
    block_id: str = None
    body: str = None
    body_hash: str = None
    bounce: bool = None
    bounced: bool = None
    chain_order: str = None
    code: str = None
    code_hash: str = None
    created_at: int = None
    created_at_string: str = None
    created_lt: int = attrs.field(converter=hex_converter, default=None)
    data: str = None
    data_hash: str = None
    dst_account: AccountData = None
    dst_transaction: 'TransactionData' = None
    dst_workchain_id: int = None
    fwd_fee: int = attrs.field(converter=hex_converter, default=None)
    ihr_disabled: bool = None
    ihr_fee: int = attrs.field(converter=hex_converter, default=None)
    import_fee: int = attrs.field(converter=hex_converter, default=None)
    library: str = None
    library_hash: str = None
    proof: str = None
    split_depth: int = None
    src_account: AccountData = None
    src_transaction: 'TransactionData' = None
    src_workchain_id: int = None
    tick: bool = None
    tock: bool = None
    value: int = attrs.field(converter=hex_converter, default=None)
    value_other: list[OtherCurrencyData] = None
    dst_transaction_id: str = None  # not exists in GraphQL
    src_transaction_id: str = None  # not exists in GraphQL


@attrs.define(frozen=True)
class TransactionActionData:
    action_list_hash: str
    msgs_created: int
    no_funds: bool
    result_code: int
    skipped_actions: int
    spec_actions: int
    status_change: int
    success: bool
    tot_actions: int
    tot_msg_size_bits: int
    tot_msg_size_cells: int
    valid: bool
    result_arg: int = None
    status_change_name: str = None
    total_action_fees: int = attrs.field(converter=hex_converter, default=None)
    total_fwd_fees: int = attrs.field(converter=hex_converter, default=None)


@attrs.define(frozen=True)
class TransactionBounceData:
    bounce_type: int
    bounce_type_name: str
    msg_size_bits: int
    msg_size_cells: int
    fwd_fees: int = attrs.field(converter=hex_converter, default=None)
    msg_fees: int = attrs.field(converter=hex_converter, default=None)
    req_fwd_fees: int = attrs.field(converter=hex_converter, default=None)


@attrs.define(frozen=True)
class TransactionComputeData:
    compute_type: int
    compute_type_name: str
    account_activated: bool = None
    exit_arg: int = None
    exit_code: int = None
    gas_credit: int = None
    gas_fees: int = attrs.field(converter=hex_converter, default=None)
    gas_limit: int = None
    gas_used: int = None
    mode: int = None
    msg_state_used: bool = None
    skipped_reason: int = None
    skipped_reason_name: str = None
    success: bool = None
    vm_final_state_hash: str = None
    vm_init_state_hash: str = None
    vm_steps: int = None


@attrs.define(frozen=True)
class TransactionCreditData:
    credit: int = attrs.field(converter=hex_converter)
    due_fees_collected: int = attrs.field(converter=hex_converter, default=None)
    credit_other: list[OtherCurrencyData] = None


@attrs.define(frozen=True)
class TransactionSplitInfoData:
    acc_split_depth: int
    cur_shard_pfx_len: int
    sibling_addr: str
    this_addr: str


@attrs.define(frozen=True)
class TransactionStorageData:
    status_change: int
    status_change_name: str
    storage_fees_collected: int = attrs.field(converter=hex_converter)
    storage_fees_due: int = attrs.field(converter=hex_converter, default=None)


@attrs.define(frozen=True)
class TransactionData(_GraphQLMeta):
    id: str
    aborted: bool
    account_addr: str
    balance_delta: int = attrs.field(converter=hex_converter)
    boc: str
    compute: TransactionComputeData
    credit_first: bool
    destroyed: bool
    end_status: int
    end_status_name: str
    in_msg: str
    lt: int = attrs.field(converter=hex_converter)
    new_hash: str
    now: int
    old_hash: str
    orig_status: int
    orig_status_name: str
    out_msgs: list[str]
    outmsg_cnt: int
    prev_trans_hash: str
    prev_trans_lt: int = attrs.field(converter=hex_converter)
    status: int
    status_name: str
    total_fees: int = attrs.field(converter=hex_converter)
    tr_type: int
    tr_type_name: str
    workchain_id: int
    account: AccountData = None
    action: TransactionActionData = None
    balance_delta_other: list[OtherCurrencyData] = None
    block: BlockData = None
    block_id: str = None
    bounce: TransactionBounceData = None
    chain_order: str = None
    credit: TransactionCreditData = None
    ext_in_msg_fee: int = attrs.field(converter=hex_converter, default=None)
    in_message: MessageData = None
    installed: bool = None
    now_string: str = None
    out_messages: list[MessageData] = None
    prepare_transaction: str = None
    proof: str = None
    split_info: TransactionSplitInfoData = None
    storage: TransactionStorageData = None
    total_fees_other: list[OtherCurrencyData] = None
    tt: str = None
