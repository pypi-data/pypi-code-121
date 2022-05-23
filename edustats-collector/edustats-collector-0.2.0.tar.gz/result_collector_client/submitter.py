import os
from result_collector_client.collector import CollectorClient
from result_collector_client.models import (
    Assignment,
    Exercise,
    Result,
    ResultWithStudentEmail,
)
import re


is_url_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE,
)


def get_env_vars():
    result_logger_url = os.environ.get('RESULT_LOGGER_URL')
    result_logger_username = os.environ.get('RESULT_LOGGER_USERNAME')
    result_logger_token = os.environ.get('RESULT_LOGGER_TOKEN')
    result_logger_lesson_id = os.environ.get('RESULT_LOGGER_LESSON_ID')
    assert result_logger_url, 'RESULT_LOGGER_URL cannot be empty/missing'
    assert (
        result_logger_username
    ), 'RESULT_LOGGER_USERNAME cannot be empty/missing'
    assert result_logger_token, 'RESULT_LOGGER_TOKEN cannot be empty/missing'
    assert (
        result_logger_lesson_id
    ), 'RESULT_LOGGER_LESSON_ID cannot be empty/missing'
    result_logger_lesson_id = int(result_logger_lesson_id)
    return (
        result_logger_url,
        result_logger_username,
        result_logger_token,
        result_logger_lesson_id,
    )


def submit(
    *,
    assignment: Assignment,
    exercise: Exercise,
    student_email: str,
    score: int | None = None,
    artifact: str | None = None,
    backlink: str = None,
):
    (
        result_logger_url,
        result_logger_username,
        result_logger_token,
        result_logger_lesson_id,
    ) = get_env_vars()

    if backlink is not None:
        if re.match(is_url_regex, backlink) is None:
            backlink = None

    client = CollectorClient(
        url=result_logger_url,
        auth={
            'username': result_logger_username,
            'token': result_logger_token,
        },
        ignore_errors=False,
    )
    assignment.lesson = result_logger_lesson_id
    assignment = assignment.get_or_create(client=client)

    exercise.assignment = assignment.id
    exercise = exercise.get_or_create(client=client)

    if backlink is not None:
        result = ResultWithStudentEmail(
            student=student_email,
            exercise=exercise.id,
            backlink=backlink,
        )
    else:
        result = ResultWithStudentEmail(
            student=student_email,
            exercise=exercise.id,
        )

    if score is not None:
        result.score = score
    if artifact is not None:
        result.artifact = artifact
    res = result.create(client=client, result_class=Result)
    return res
