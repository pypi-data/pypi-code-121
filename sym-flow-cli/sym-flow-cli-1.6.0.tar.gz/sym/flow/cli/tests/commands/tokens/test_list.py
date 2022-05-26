from typing import List
from unittest.mock import patch
from uuid import UUID

import pytest

from sym.flow.cli.commands.tokens.issue import to_timedelta
from sym.flow.cli.commands.tokens.list import get_tokens_data, get_user
from sym.flow.cli.errors import InvalidExpiryError
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.constants import DEFAULT_API_URL
from sym.flow.cli.helpers.utils import human_friendly, utc_to_local
from sym.flow.cli.models import User
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.tokens import SymTokenFactory
from sym.flow.cli.tests.factories.users import UserFactory


class TestTokensList:
    @pytest.fixture
    def tokens(self):
        yield SymTokenFactory.create_batch(3)

    @pytest.fixture
    def users(self):
        yield UserFactory.create_batch(2)

    def test_get_tokens_data(self, tokens, users, global_options):
        with patch(
            "sym.flow.cli.helpers.api.SymAPI.get_tokens",
            return_value=tokens,
        ):
            # API will be called twice per token, because factory generates 6 users
            with patch(
                "sym.flow.cli.helpers.api.SymAPI.get_user_by_id",
                side_effect=[users[0], users[1]] * 3,
            ):
                table_data = get_tokens_data(global_options.sym_api)

        assert table_data.pop(0) == [
            "Token ID",
            "User",
            "Created By",
            "Expires At",
            "Last Used",
            "Label",
        ]
        for i, row in enumerate(table_data):
            assert row == [
                tokens[i].identifier,
                users[0].sym_identifier,
                users[1].sym_identifier,
                human_friendly(utc_to_local(tokens[i].expires_at)),
                human_friendly(utc_to_local(tokens[i].updated_at)),
                tokens[i].label,
            ]

    def test_get_user(self, users: List[User], global_options):
        user_cache = {}
        with patch(
            "sym.flow.cli.helpers.api.SymAPI.get_user_by_id",
            side_effect=[users[0], users[1]],
        ) as mock_sym_api_get:
            # This should return side_effect 1 of the patch
            assert (
                get_user(UUID(users[0].id), user_cache, global_options.sym_api)
                == users[0]
            )

            # API should not be called. We will assert the number of calls at the end
            assert (
                get_user(UUID(users[0].id), user_cache, global_options.sym_api)
                == users[0]
            )

            # This should return side_effect 2 of the patch
            assert (
                get_user(UUID(users[1].id), user_cache, global_options.sym_api)
                == users[1]
            )

            # only called twice, once per unique user.
            assert mock_sym_api_get.call_count == 2
