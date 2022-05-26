import coiled
import pytest
from distributed.utils_test import loop  # noqa: F401

pytestmark = pytest.mark.test_group("test_public_configs")


@pytest.fixture
async def three_clouds(
    cleanup, sample_user, jess_from_fedex, remote_access_url, settings, base_user_token
):
    """
    Return a tuple of three clouds, one for coiled, one for jess,
    and one for fedex. Each will have one environment and one configuration
    """
    # coiled is not a member of FedEx
    coiled_user = sample_user.user
    jess = jess_from_fedex

    async with coiled.Cloud(
        user=coiled_user.username,
        token=base_user_token,
        asynchronous=True,
    ) as my_cloud:
        async with coiled.Cloud(
            user=jess.username,
            token=jess.auth_token.key,
            asynchronous=True,
        ) as jesss_cloud:
            async with coiled.Cloud(
                user=jess.username,
                token=jess.auth_token.key,
                account="fedex",
                asynchronous=True,
            ) as fedex_cloud:
                await my_cloud.create_software_environment(
                    name="env1", container="daskdev/dask:latest"
                )
                await jesss_cloud.create_software_environment(
                    name="env1", container="daskdev/dask:latest"
                )
                await fedex_cloud.create_software_environment(
                    name="fedex/env1", container="daskdev/dask:latest"
                )
                yield my_cloud, jesss_cloud, fedex_cloud


@pytest.mark.asyncio
async def test_can_create_software_environment_using_full_name_or_short_name(
    three_clouds,
):
    _, _, fedex = three_clouds

    # First with fully qualified name
    await fedex.create_software_environment(
        name="fedex/goodstuff", container="daskdev/dask:latest"
    )
    configs = await fedex.list_software_environments()
    e = configs["fedex/goodstuff"]
    assert e["account"] == "fedex"

    # Then with short name
    await fedex.create_software_environment(
        name="goodstuff2", container="daskdev/dask:latest"
    )
    configs = await fedex.list_software_environments()
    e = configs["fedex/goodstuff2"]
    assert e["account"] == "fedex"


@pytest.mark.asyncio
async def test_can_create_software_environment_in_different_account_when_member(
    three_clouds,
):
    _, jesss_cloud, fedex = three_clouds
    # jess is a member of fedex, so she should be allowed to create in that account
    await jesss_cloud.create_software_environment(
        name="fedex/goodenv", container="daskdev/dask:latest"
    )
    jess_envs = await jesss_cloud.list_software_environments()
    fedex_envs = await fedex.list_software_environments()
    assert "fedex/goodenv" not in jess_envs
    assert "fedex/goodenv" in fedex_envs
    e = fedex_envs["fedex/goodenv"]
    assert e["account"] == "fedex"


@pytest.mark.asyncio
async def test_cannot_create_software_environment_in_foreign_account(three_clouds):
    # "coiled" is not a member of fedex or jesss
    my_cloud, jesss_cloud, _ = three_clouds

    with pytest.raises(ValueError, match="Unauthorized"):
        await my_cloud.create_software_environment(
            name="fedex/invasive_env", container="daskdev/dask:latest"
        )
