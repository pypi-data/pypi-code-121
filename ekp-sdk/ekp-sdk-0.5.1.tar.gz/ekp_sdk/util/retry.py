from aioretry import RetryInfo


def default_retry_policy(info: RetryInfo):
    print(f"🚨 {info.exception}")
    return (info.fails >= 8), [0, 0.5, 2, 5, 10, 15, 20, 30, 60][info.fails - 1]
