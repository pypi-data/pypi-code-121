from typing import Optional


def get_parent_job_id_from_job_tree(job_tree) -> Optional[str]:
    """job_treeから親のjob_idを取得します。
    親のジョブがない場合はNoneを返します。

    Args:
        job_tree:
    Returns:
        親ジョブのjob_id。親ジョブがなければNone。
    """
    tmp_list = job_tree.split("/")
    if len(tmp_list) <= 2:
        # "org/job_id" の場合はルートジョブなのでparent_job_idはNone
        return None
    parent_job_id = tmp_list[len(tmp_list) - 2]
    return parent_job_id
