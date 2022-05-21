from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Optional

import pandas

import annoworkcli
from annoworkcli.common.cli import COMMAND_LINE_ERROR_STATUS_CODE, OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.expected_working_time.list_expected_working_time import ListExpectedWorkingTime

logger = logging.getLogger(__name__)


def get_weekly_expected_working_hours_df(
    expected_working_times: list[dict[str, Any]], workspace_members: list[dict[str, Any]]
) -> pandas.DataFrame:
    """週単位の予定稼働時間が格納されたDataFrameを生成します。

    Args:
        expected_working_times: 予定稼働時間情報。date, workspace_member_id, expected_working_hours を参照します。
        workspace_members: ワークスペースメンバ情報。workspace_member_id, user_id, username を参照します。

    Returns:
        以下の列を返すDataFrame。
            "workspace_member_id", "user_id","username", "start_date", "end_date", "expected_working_hours"
    """
    df = pandas.DataFrame(expected_working_times)
    # 1週間ごとに集計する（日曜日始まり, 日曜日がindexになっている）
    df["date"] = pandas.to_datetime(df["date"])
    df_weekly = df.groupby("workspace_member_id").resample("W", on="date", label="left", closed="left").sum()
    df_weekly.reset_index(inplace=True)

    # 1週間の始まり（日曜日）と終わり（土曜日）の日付列を設定
    df_weekly.rename(columns={"date": "start_date"}, inplace=True)
    df_weekly["end_date"] = df_weekly["start_date"] + pandas.Timedelta(days=6)
    # pandas.Timestamp型をstr型に変換する
    df_weekly["start_date"] = df_weekly["start_date"].dt.date.apply(lambda e: e.isoformat())
    df_weekly["end_date"] = df_weekly["end_date"].dt.date.apply(lambda e: e.isoformat())

    # 予定稼働時間が0の行は不要なので、除外する
    df_weekly = df_weekly.query("expected_working_hours > 0")

    df_workspace_member = pandas.DataFrame(workspace_members)

    df = df_weekly.merge(df_workspace_member, on="workspace_member_id", how="left")
    df.sort_values(["user_id", "start_date"], inplace=True)

    return df[["workspace_member_id", "user_id", "username", "start_date", "end_date", "expected_working_hours"]]


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    start_date: Optional[str] = args.start_date
    end_date: Optional[str] = args.end_date

    command = " ".join(sys.argv[0:3])
    if all(v is None for v in [user_id_list, start_date, end_date]):
        print(f"{command}: error: '--start_date'や'--user_id'などの絞り込み条件を1つ以上指定してください。", file=sys.stderr)
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    main_obj = ListExpectedWorkingTime(annowork_service=annowork_service, workspace_id=args.workspace_id)

    if user_id_list is not None:
        expected_working_times = main_obj.get_expected_working_times_by_user_id(
            user_id_list=user_id_list, start_date=start_date, end_date=end_date
        )
    else:
        expected_working_times = main_obj.get_expected_working_times(start_date=start_date, end_date=end_date)

    if len(expected_working_times) == 0:
        logger.warning(f"予定稼働時間情報0件なので、出力しません。")
        return

    df = get_weekly_expected_working_hours_df(expected_working_times, main_obj.workspace_members)

    logger.info(f"{len(df)} 件の週単位の予定稼働時間情報を出力します。")

    if OutputFormat(args.format) == OutputFormat.CSV:
        print_csv(df, output=args.output)

    elif OutputFormat(args.format) == OutputFormat.JSON:
        print_json(df.to_dict("records"), is_pretty=True, output=args.output)
    else:
        logger.error("`--format`が対象外でした。")


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="集計対象のユーザID")

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

    parser.add_argument("-o", "--output", type=Path, help="出力先")
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=[e.value for e in OutputFormat],
        help="出力先のフォーマット",
        default=OutputFormat.CSV.value,
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list_weekly"
    subcommand_help = "予定稼働時間の一覧を週ごと（日曜日始まり）に出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
