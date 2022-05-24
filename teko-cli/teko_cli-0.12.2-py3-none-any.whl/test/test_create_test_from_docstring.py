import json

import pytest

from teko.services.jira_export_test.test_case_service import TestCaseService


@pytest.mark.parametrize(
    "test_id, docstring, expect_test_case, test_index",
    [
        (1,
         """
                ::JIRA
                name, objective: [
                    ('test_plus_two_number_1_2_new', 'make sure 1 + 1 == 2'),
                    ('test_plus_two_number_2_2_4_new', 'make sure 2 + 2 = 4')
                ]
                issueLinks: TESTING-9, TESTING-10
                precondition: Nothing
                confluenceLinks: https://confluence.teko.vn/display/EP/Archive, https://confluence.teko.vn/display/EP/Data+Flow+Diagrams
                webLinks: Dungntc.com, google.com
                folder: /Mkt Portal Test/Campaign msg test
                priority: Normal
                plan: ''
            """,
         {
             "confluenceLinks": [
                 "https://confluence.teko.vn/display/EP/Archive",
                 "https://confluence.teko.vn/display/EP/Data+Flow+Diagrams"
             ],
             "folder": "/Mkt Portal Test/Campaign msg test",
             "issueLinks": [
                 "TESTING-9",
                 "TESTING-10"
             ],
             "name": "test_plus_two_number_2_2_4_new",
             "objective": "make sure 2 + 2 = 4",
             "precondition": "Nothing",
             "priority": "Normal",
             "testScript": {
                 "text": "''",
                 "type": "PLAIN_TEXT"
             },
             "webLinks": [
                 "Dungntc.com",
                 "google.com"
             ]
         }, 1),
        (2,
         """
                ::JIRA
                name, objective, precondition: [
                    ('test_plus_two_number_1_2_new', 'make sure 1 + 1 == 2', 'precond 1'),
                    ('test_plus_two_number_2_2_4_new', 'make sure 2 + 2 = 4', 'precond 2')
                ]
                issueLinks: TESTING-9, TESTING-10
                confluenceLinks: https://confluence.teko.vn/display/EP/Archive, https://confluence.teko.vn/display/EP/Data+Flow+Diagrams
                webLinks: Dungntc.com, google.com
                folder: /Mkt Portal Test/Campaign msg test
                priority: Normal
                plan: ''
            """,
         {
             "confluenceLinks": [
                 "https://confluence.teko.vn/display/EP/Archive",
                 "https://confluence.teko.vn/display/EP/Data+Flow+Diagrams"
             ],
             "folder": "/Mkt Portal Test/Campaign msg test",
             "issueLinks": [
                 "TESTING-9",
                 "TESTING-10"
             ],
             "name": "test_plus_two_number_2_2_4_new",
             "objective": "make sure 2 + 2 = 4",
             "precondition": "precond 2",
             "priority": "Normal",
             "testScript": {
                 "text": "''",
                 "type": "PLAIN_TEXT"
             },
             "webLinks": [
                 "Dungntc.com",
                 "google.com"
             ]
         }, 1),
        (3,
         """
                ::JIRA
                objective, name, precondition: [
                    ('make sure 1 + 1 == 2', 'test_plus_two_number_1_2_new', 'precond 1'),
                    ('make sure 2 + 2 = 4', 'test_plus_two_number_2_2_4_new', 'precond 2')
                ]
                issueLinks: TESTING-9, TESTING-10
                precondition: Nothing
                confluenceLinks: https://confluence.teko.vn/display/EP/Archive, https://confluence.teko.vn/display/EP/Data+Flow+Diagrams
                webLinks: Dungntc.com, google.com
                folder: /Mkt Portal Test/Campaign msg test
                priority: Normal
                plan: ''
            """,
         {
             "confluenceLinks": [
                 "https://confluence.teko.vn/display/EP/Archive",
                 "https://confluence.teko.vn/display/EP/Data+Flow+Diagrams"
             ],
             "folder": "/Mkt Portal Test/Campaign msg test",
             "issueLinks": [
                 "TESTING-9",
                 "TESTING-10"
             ],
             "name": "test_plus_two_number_2_2_4_new",
             "objective": "make sure 2 + 2 = 4",
             "precondition": "precond 2",
             "priority": "Normal",
             "testScript": {
                 "text": "''",
                 "type": "PLAIN_TEXT"
             },
             "webLinks": [
                 "Dungntc.com",
                 "google.com"
             ]
         }, 1),
        (4,
         """
                ::JIRA
                name: ['test_1>=1', 'test_2>1']
                issueLinks: TESTING-9, TESTING-10
                objective: ['make sure 1 >= 1', 'make sure 2 > 1']
                precondition: Nothing
                confluenceLinks: https://confluence.teko.vn/display/EP/Archive, https://confluence.teko.vn/display/EP/Data+Flow+Diagrams
                webLinks: Dungntc.com, google.com
                folder: /Mkt Portal Test/Campaign msg test
                priority: Normal
                plan: ''
            """,
         {
             "confluenceLinks": [
                 "https://confluence.teko.vn/display/EP/Archive",
                 "https://confluence.teko.vn/display/EP/Data+Flow+Diagrams"
             ],
             "folder": "/Mkt Portal Test/Campaign msg test",
             "issueLinks": [
                 "TESTING-9",
                 "TESTING-10"
             ],
             "name": "test_1>=1",
             "objective": "make sure 1 >= 1",
             "precondition": "Nothing",
             "priority": "Normal",
             "testScript": {
                 "text": "''",
                 "type": "PLAIN_TEXT"
             },
             "webLinks": [
                 "Dungntc.com",
                 "google.com"
             ]
         }, 0
         ),
        (5,
         """
                ::JIRA
                name: test_create_campaign_msg_fail_when_duplicate_brand_docstring
                issueLinks: TESTING-9
                objective: Make sure that not allow create message when exists msg with same brand
                precondition: Has an message template from User Notification service
                confluenceLinks: https://confluence.teko.vn/display/EP/Archive, https://confluence.teko.vn/display/EP/Data+Flow+Diagrams
                folder: /Mkt Portal Test/Campaign msg test
                priority: Normal
            """,
         {
             "confluenceLinks": ['https://confluence.teko.vn/display/EP/Archive',
                                 'https://confluence.teko.vn/display/EP/Data+Flow+Diagrams'],
             "folder": "/Mkt Portal Test/Campaign msg test",
             "issueLinks": [
                 "TESTING-9"
             ],
             "name": "test_create_campaign_msg_fail_when_duplicate_brand_docstring",
             "objective": "Make sure that not allow create message when exists msg with same brand",
             "precondition": "Has an message template from User Notification service",
             "priority": "Normal",
             "webLinks": [],
             "testScript": {}
         }, None
         )
    ]
)
def test_create_test_from_docstring(test_id, docstring, expect_test_case, test_index):
    test_case = TestCaseService().create_test_case_from_docstring(docstring=docstring, test_index=test_index,
                                                                  function_name='test_123',
                                                                  test_id=1)

    for actual_key, actual_value in test_case.to_dict().items():
        assert actual_key in expect_test_case.keys()
        assert actual_value == expect_test_case[actual_key]
