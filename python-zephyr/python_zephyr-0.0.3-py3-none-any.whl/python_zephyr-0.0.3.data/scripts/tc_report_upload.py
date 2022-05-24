#!python
import zephyr.tc_mgmt as tc_lib


def main():
    """
    Main function.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Upload test results to Zephyr Test Database.')
    parser.add_argument(
        '--token', help='Zephyr API token file.', required=True)
    parser.add_argument(
        '--sw_ver', help='Software version of the DUT. (Format: XXXXXXXX_XXXXXXXX)', required=True)
    parser.add_argument(
        '--hw_ver', help='Hardware version of the DUT.', required=True)
    parser.add_argument(
        '--test_key', help='key of the test. (e.g. BSBS-T1)', required=True)
    parser.add_argument(
        '--test_result', help='Result of the test (PASS, FAIL, NOT EXECUTED).', required=True)
    parser.add_argument('--execution_time',
                        help='Execution time of the test.', required=True)
    parser.add_argument(
        '--log_path', help='Path to the test log.', required=True)
    parser.add_argument(
        '--comments', help='Comments to be added to the test.', required=True)
    parser.add_argument(
        '--env_name', help='Name of the test environment.', required=False)
    args = parser.parse_args()

    with open(args.token, 'r') as token_file:
        token = token_file.read().strip()

    tc_mgmt = tc_lib.TestManagement(token)
    tc_mgmt.upload_results(args.sw_ver, args.hw_ver, args.test_key, tc_lib.TestVerdicts[args.test_result],
                           int(args.execution_time), args.log_path, args.comments, args.env_name)


if __name__ == "__main__":
    main()
