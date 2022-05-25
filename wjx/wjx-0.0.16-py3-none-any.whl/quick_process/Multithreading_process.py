def split_tasks_list(
    task_list: list,
    number_of_thread=4,
):
    """将任务列表平均分为number_of_thread+1个,用于多线程_thread

    Args:
        task_list: list类型,原始人任务列表
        number_of_thread= int类型,线程数-1

    Returns:
        平均分后的列表，其中包含多个子列表

    """

    # 将任务分为number_of_thread个子任务
    tasks_list = []
    for n in range(number_of_thread + 1):
        tasks_list.append(task_list[(len(task_list) // number_of_thread) * n:(len(task_list) // number_of_thread) * (n + 1)])

    return tasks_list
