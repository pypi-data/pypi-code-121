from typing import Dict

import aiofiles
import dict_tools.utils


async def generate_key(hub, plugin: str):
    ret = hub.crypto[plugin].generate_key()
    return await hub.pop.loop.unwrap(ret)


async def encrypt(hub, data, key: str, plugin: str):
    """
    Call the named crypto_plugin.
    Pass it's "encrypt" function the raw data and the encryption key
    return the encrypted data
    """
    ret = hub.crypto[plugin].encrypt(data, key)
    return await hub.pop.loop.unwrap(ret)


async def decrypt(hub, data: bytes, key: str, plugin: str):
    """
    Call the named crypto_plugin.
    Pass it's "decrypt" function the encrypted data and the decryption key
    return the raw decrypted data
    """
    ret = hub.crypto[plugin].decrypt(data, key)
    return await hub.pop.loop.unwrap(ret)


async def encrypt_file(
    hub,
    crypto_plugin: str,
    acct_file: str,
    acct_key: str = None,
    output_file: str = None,
    render_pipe: str = "yaml",
):
    """
    Serialize and encrypt the given data then write it to a file
    """
    # Parse the acct_file through the render pipes
    data = await hub.rend.init.parse(acct_file, pipe=render_pipe)

    if acct_key is None:
        acct_key = await hub.crypto.init.generate_key(plugin=crypto_plugin)

    encrypted: bytes = await hub.crypto.init.encrypt(
        plugin=crypto_plugin, data=data, key=acct_key
    )

    if not output_file:
        output_file = f"{acct_file}.{crypto_plugin}"

    async with aiofiles.open(output_file, "wb+") as fh_:
        await fh_.write(encrypted)

    hub.log.info(f"New encrypted file created in {output_file}")

    return acct_key


async def decrypt_file(
    hub,
    crypto_plugin: str,
    acct_file: str,
    acct_key: str = None,
    render_pipe: str = None,
) -> Dict:
    """
    Read a file and decrypt and deserialize the data
    """
    async with aiofiles.open(acct_file, "rb") as fh_:
        raw = await fh_.read()

    if acct_key:
        # Use the acct key to decrypt the data, it was already rendered when it was encrypted
        return await hub.crypto.init.decrypt(
            plugin=crypto_plugin, data=raw, key=acct_key
        )
    else:
        # If no acct key was provided then pass the raw data to the render pipes
        return await hub.rend.init.parse_bytes(raw, pipe=render_pipe)


def dump(hub, data: Dict) -> bytes:
    """
    Serialize a python object using the acct serial plugin
    """
    return hub.serial[hub.acct.SERIAL_PLUGIN].dump(data)


def load(hub, raw: bytes) -> Dict:
    """
    De-serialize a bytes string to a python object using the acct serial plugin
    """
    data = hub.serial[hub.acct.SERIAL_PLUGIN].load(raw)
    return dict_tools.utils.decode_dict(data)
