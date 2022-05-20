# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import socket
import typing
from ctypes import (CDLL, CFUNCTYPE, POINTER, byref, c_char, c_char_p, c_int,
                    c_uint, c_ulong, c_void_p)
from dataclasses import fields
from typing import List, Tuple, Union

from .. import data
from .enums import AttributeEnum, CallBackEnum, EventEnum, RightsEnum

SDK_FILE = './aw64.dll'
SDK = CDLL(SDK_FILE)
AW_BUILD = 134 # AW 7.0
AW_CALLBACK = CFUNCTYPE(None)

def aw_int_set(attribute: AttributeEnum, value: int) -> None:
    """
    Sets an initialization attribute.

    Args:
        AttributeEnum (AttributeEnum): The attribute name.
        value (int): The attribute value.

    Raises:
        Exception: If the attribute could not be set.
    """
    rc = SDK.aw_int_set(attribute.value, value)

    if rc:
        raise Exception(f"Failed to set initialization attribute: {rc}")

def aw_string_set(attribute: AttributeEnum, value: str) -> None:
    """
    Sets an initialization attribute.

    Args:
        attribute (AttributeEnum): The attribute name.
        value (str): The attribute value.

    Raises:
        Exception: If the attribute could not be set.
    """
    rc = SDK.aw_string_set(attribute.value, value.encode('utf-8'))

    if rc:
        raise Exception(f"Failed to set initialization attribute: {rc}")

def aw_address(session_id: int) -> data.AddressData:
    """
    Returns the IP address of the provided session.

    Args:
        session_id (int): The session ID to get the IP address of.

    Returns:
        data.AddressData: The IP address of the session.
    """
    rc = SDK.aw_address(session_id)

    if rc != 0:
        raise Exception(f'Failed to get the IP address of the session. Error code: {rc}')

    return data.AddressData(
        aw_int(AttributeEnum.AW_AVATAR_SESSION.value),
        aw_int(AttributeEnum.AW_AVATAR_ADDRESS.value)
    )

def aw_avatar_click(session_id: int) -> None:
    """
    Sends a click event to the avatar. Simulates a left click.
    AW_EVENT_AVATAR_CLICK is triggered.

    Args:
        session_id (int): The session ID of the avatar to click.
    """
    rc = SDK.aw_avatar_click(session_id)

    if rc != 0:
        raise Exception(f'Failed to click the avatar. Error code: {rc}')

def aw_avatar_location(
    citizen: typing.Optional[int] = None,
    session: typing.Optional[int] = None,
    name: typing.Optional[str] = None
) -> None:
    """
    Queries the location of an avatar.
    Returns the location via the callback.
    Only one of these parameters can be specified.

    Args:
        citizen (typing.Optional[int], optional): The citizen ID. Defaults to None.
        session (typing.Optional[int], optional): The session ID. Defaults to None.
        name (typing.Optional[str], optional): The name of the avatar. Defaults to None.

    Raises:
        Exception: If the location could not be queried.
    """
    rc = SDK.aw_avatar_location(
        citizen,
        session,
        name.encode('utf-8') if name else None
    )

    if rc:
        raise Exception(f"Failed to query avatar location: {rc}")

def aw_avatar_reload(citizen: int = 0, session: int = 0) -> None:
    """
    If the avatar exists and call was successful send AW_EVENT_AVATAR_RELOAD to all users in the world.
    Only one of the parameters can be set to a non-zero/non-null value. 

    Args:
        citizen (int, optional): The citizen ID to reload the avatar of. Defaults to 0.
        session (int, optional): The session ID to reload the avatar of. Defaults to 0.
    """
    if citizen is None and session is None:
        raise Exception('One of the parameters must be set to a non-zero/non-null value.')

    rc = SDK.aw_avatar_reload(citizen, session)

    if rc != 0:
        raise Exception(f'Failed to reload the avatar. Error code: {rc}')

def aw_avatar_set(session_id: int) -> None:
    """
    Sets the avatar with the provided session ID.

    Args:
        session_id (int): The session ID of the avatar to set.
    """
    rc = SDK.aw_avatar_set(session_id)

    if rc != 0:
        raise Exception(f'Failed to set the avatar. Error code: {rc}')

def aw_bool(attribute: AttributeEnum) -> bool:
    """
    Returns the value of a boolean attribute

    Args:
        attribute (AttributeEnum): The attribute to get the value of.

    Returns:
        bool: The value of the attribute.
    """
    return bool(SDK.aw_bool(attribute.value))

def aw_bool_set(attribute: AttributeEnum, value: bool) -> None:
    """
    Sets an initialization attribute.

    Args:
        attribute (AttributeEnum): The attribute name.
        value (bool): The attribute value.

    Raises:
        Exception: If the attribute could not be set.
    """
    rc = SDK.aw_bool_set(attribute.value, value)

    if rc:
        raise Exception(f"Failed to set initialization attribute: {rc}")

def aw_botgram_send(text: str, citizen: int) -> None:
    """
    Sends a botgram to the bots of the provided citizen.
    
    Args:
        text (str): The text to send.
        citizen (int): The citizen ID to send the botgram to.
    """
    aw_string_set(AttributeEnum.AW_BOTGRAM_TEXT, text)
    aw_int_set(AttributeEnum.AW_BOTGRAM_TO, citizen)

    rc = SDK.aw_botgram_send()

    if rc != 0:
        raise Exception(f'Failed to send the botgram. Error code: {rc}')

def aw_botmenu_send(bot_menu: data.BotMenuData) -> None:
    """
    Builds and sends a botmenu to the defined session.

    Raises:
        Exception: If the botmenu could not be sent.

    Args:
        bot_menu (data.BotMenuData): The botmenu data.
    """
    aw_int_set(AttributeEnum.AW_BOTMENU_TO_SESSION, bot_menu.to_session)
    aw_string_set(AttributeEnum.AW_BOTMENU_QUESTION, bot_menu.question)
    aw_string_set(AttributeEnum.AW_BOTMENU_ANSWER, bot_menu.answer)

    rc = SDK.aw_botmenu_send()
    
    if rc != 0:
        raise Exception(f'Failed to send the botmenu. Error code: {rc}')

def aw_callback(callback: CallBackEnum) -> c_void_p:
    """
    Returns the address of a callback function.

    Args:
        callback (CallBackEnum): The callback to get the address of.

    Returns:
        c_void_p: The address of the callback.
    """
    return SDK.aw_callback(callback.value)

def aw_callback_set(callback: CallBackEnum, handler: AW_CALLBACK) -> None:
    """
    Set a callback to the specified handler.

    Args:
        callback (CallBackEnum): The callback to set.
        handler (AW_CALLBACK): The callback handler.
    """
    rc = SDK.aw_callback_set(callback.value, handler)

    if rc != 0:
        raise Exception(f'Failed to set the callback. Error code: {rc}')

def aw_camera_set(session_id: int, camera_set: data.CameraSetData) -> None:
    """
    Sets the camera of the specified session.

    Args:
        session_id (int): The session ID of the avatar to set the camera of.
        camera_set (data.CameraSetData): The camera data.
    
    Raises:
        Exception: If the camera could not be set.
    """
    from .write_data import write_data
    for field in fields(camera_set):
        value = getattr(camera_set, field.name, None)
        attr = getattr(AttributeEnum, f'AW_CAMERA_{field.name.upper()}')

        if value is not None:
            write_data(attr, value)
    
    rc = SDK.aw_camera_set(session_id)

    if rc != 0:
        raise Exception(f'Failed to set the camera. Error code: {rc}')

def aw_cav_change(cav_change: data.CavChangeData) -> None:
    """
    Changes the CAV of the specified citizen.

    Args:
        cav_change (data.CavChangeData): The CAV change data.

    Raises:
        Exception: If the CAV could not be changed.
    """
    aw_int_set(AttributeEnum.AW_CAV_CITIZEN, cav_change.citizen)
    aw_int_set(AttributeEnum.AW_CAV_SESSION, cav_change.session)
    aw_data_set(AttributeEnum.AW_CAV_DEFINITION, cav_change.definition)

    rc = SDK.aw_cav_change()

    if rc != 0:
        raise Exception(f'Failed to change the CAV. Error code: {rc}')
    
def aw_cav_delete(cav_delete: data.CavDeleteData) -> None:
    """
    Deletes the CAV of the specified citizen.

    Args:
        cav_delete (data.CavDeleteData): The CAV delete data.

    Raises:
        Exception: If the CAV could not be deleted.
    """
    aw_int_set(AttributeEnum.AW_CAV_CITIZEN, cav_delete.citizen)
    aw_int_set(AttributeEnum.AW_CAV_SESSION, cav_delete.session)

    rc = SDK.aw_cav_delete()

    if rc != 0:
        raise Exception(f'Failed to delete the CAV. Error code: {rc}')

def aw_cav_request(citizen: int, session: int) -> None:
    """
    Queries the universe for the CAV of the specified citizen.

    Args:
        citizen (int): The citizen ID to query the CAV of.
        session (int): The session ID to query the CAV of.

    Raises:
        Exception: If the CAV could not be requested.
    """    
    rc = SDK.aw_cav_request(citizen, session)

    if rc != 0:
        raise Exception(f'Failed to request the CAV. Error code: {rc}')

def aw_cell_next(combine: bool = False, iterator: data.CellIteratorData = None) -> None:
    """
    Queries the next cell in the cell iterator.
    If combine is set to true this call will batch multiple cells.
    A specific cell can be set by setting the iterator to zero and z and x cell coordinates.

    Args:
        combine (bool, optional): Whether to combine multiple cells. Defaults to False.
        iterator (data.CellIteratorData, optional):  The cell iterator. Defaults to None.

    Raises:
        Exception: If the cell could not be queried.
    """    
    if iterator:
        aw_int_set(AttributeEnum.AW_CELL_ITERATOR, iterator.iterator)

    aw_bool_set(AttributeEnum.AW_CELL_COMBINE, combine)
    rc = SDK.aw_cell_next()

    if rc != 0:
        raise Exception(f'Failed to get the next cell. Error code: {rc}')

def aw_check_right(citizen: int, right: str) -> bool:
    """
    Checks if the citizen has the specified right.

    Args:
        citizen (int): The citizen number to check the right of.
        right (str): A rights list.
            0    ... tourists
            any# ... citizen number
            -    ... exclusion sign
            #~#  ... citizen range
            *    ... everyone
            , blank  ... delimiters

    Example:
        "1~2300,-512~1024" 
            Grants rights to 1 to 2300
            Deny rights to 512 to 1024.

    Returns:
        bool: True if the citizen has the right, False otherwise.
    """ 
    SDK.aw_check_right.argtypes = [c_int, c_char_p]
    SDK.aw_check_right.restype = c_int

    return bool(SDK.aw_check_right(citizen, right))

def aw_check_right_all(right: str) -> bool:
    """
    Checks if all citizens have the specified right.

    Args:
        right (str): A rights list.
            0    ... tourists
            any# ... citizen number
            -    ... exclusion sign
            #~#  ... citizen range
            *    ... everyone
            , blank  ... delimiters

    Returns:
        bool: True if all citizens have the right, False otherwise.
    """
    SDK.aw_check_right_all.argtypes = [c_char_p]
    SDK.aw_check_right_all.restype = c_int

    rc = SDK.aw_check_right_all(right)

    return bool(rc)

def aw_citizen_add(citizen: data.CitizenData) -> None:
    """
    Adds a citizen to the universe.

    Args:
        citizen (CitizenAddData): The citizen data.

    Raises:
        Exception: If the citizen could not be added.
    """
    from .write_data import write_data

    for field in fields(citizen):
        value = getattr(citizen, field.name, None)
        attr = getattr(AttributeEnum, f'AW_CITIZEN_{field.name.upper()}')

        if value is not None:
            write_data(attr, value)
    
    rc = SDK.aw_citizen_add()

    if rc != 0:
        raise Exception(f'Failed to add the citizen. Error code: {rc}')

def aw_citizen_attributes_by_name(name: str) -> None:
    """
    Gets citizen attributes by name and returns via callback.

    Args:
        name (str): The citizen name to get the attributes of.

    Raises:
        Exception: If the attributes could not be requested.
    """
    SDK.aw_citizen_attributes_by_name.argtypes = [c_char_p]
    SDK.aw_citizen_attributes_by_name.restype = c_int

    rc = SDK.aw_citizen_attributes_by_name(name)

    if rc != 0:
        raise Exception(f'Failed to get the attributes of the citizen. Error code: {rc}')

def aw_citizen_attributes_by_number(citizen: int) -> None:
    """
    Gets citizen attributes by number and returns via callback.

    Args:
        citizen (int): The citizen number to get the attributes of.

    Raises
        Exception: If the attributes could not be requested.
    """
    SDK.aw_citizen_attributes_by_number.argtypes = [c_int]
    SDK.aw_citizen_attributes_by_number.restype = c_int

    rc = SDK.aw_citizen_attributes_by_number(citizen)

    if rc != 0:
        raise Exception(f'Failed to get the attributes of the citizen. Error code: {rc}')

def aw_citizen_change(citizen: data.CitizenData) -> None:
    """
    Changes the data of the specified citizen.

    Args:
        citizen (data.CitizenData): The citizen data.

    Raises:
        Exception: If the citizen could not be changed.
    """
    from .write_data import write_data

    for field in fields(citizen):
        value = getattr(citizen, field.name, None)
        attr = getattr(AttributeEnum, f'AW_CITIZEN_{field.name.upper()}')
        write_data(attr, value)
    
    rc = SDK.aw_citizen_change()

    if rc != 0:
        raise Exception(f'Failed to change the citizen. Error code: {rc}')    

def aw_citizen_delete(citizen: int) -> None:
    """
    Deletes the specified citizen.

    Args:
        citizen (int): The citizen number to delete.

    Raises:
        Exception: If the citizen could not be deleted.
    """
    SDK.aw_citizen_delete.argtypes = [c_int]
    SDK.aw_citizen_delete.restype = c_int

    rc = SDK.aw_citizen_delete(citizen)

    if rc != 0:
        raise Exception(f'Failed to delete the citizen. Error code: {rc}')

def aw_citizen_next(citizen: typing.Optional[int] = None) -> data.CitizenData:
    """
    Queries the next citizen in the citizen iterator.

    Args:
        citizen (typing.Optional[int], optional): The citizen number to start the query. Defaults to None.

    Raises:
        Exception: If the citizen could not be queried.

    Returns:
        CitizenData: The citizen data.
    """    
    from .get_data import get_data

    if citizen:
        aw_int_set(AttributeEnum.AW_CITIZEN_NUMBER, citizen)

    rc = SDK.aw_citizen_next()

    if rc != 0:
        raise Exception(f'Failed to get the next citizen. Error code: {rc}')
    
    citizen = data.CitizenData()

    for field in fields(citizen):
        attr = getattr(AttributeEnum, f'AW_CITIZEN_{field.name.upper()}')
        value = get_data(attr)
        setattr(citizen, field.name, value)

    return citizen

def aw_citizen_previous(citizen: typing.Optional[int] = None) -> data.CitizenData:
    """
    Queries the previous citizen in the citizen iterator.

    Args:
        citizen (typing.Optional[int], optional): The citizen number to start the query. Defaults to None.

    Raises:
        Exception: If the citizen could not be queried.

    Returns:
        CitizenData: The citizen data.
    """    
    from .get_data import get_data

    if citizen:
        aw_int_set(AttributeEnum.AW_CITIZEN_NUMBER, citizen)

    rc = SDK.aw_citizen_previous()

    if rc != 0:
        raise Exception(f'Failed to get the previous citizen. Error code: {rc}')
    
    citizen = data.CitizenData()

    for field in fields(citizen):
        attr = getattr(AttributeEnum, f'AW_CITIZEN_{field.name.upper()}')
        value = get_data(attr)
        setattr(citizen, field.name, value)

    return citizen

def aw_console_message(session_id: int, console_message: data.ConsoleMessageData) -> None:
    """
    Sends a console message to the specified session.

    Args:
        session_id (int): The session ID to send the message to.
        console_message (data.ConsoleMessageData): The message data.

    Raises:
        Exception: If the message could not be sent.
    """
    from .write_data import write_data

    for field in fields(console_message):
        value = getattr(console_message, field.name, None)
        attr = getattr(AttributeEnum, f'AW_CONSOLE_{field.name.upper()}')
        write_data(attr, value)
    
    rc = SDK.aw_console_message(session_id)

    if rc != 0:
        raise Exception(f'Failed to send the message. Error code: {rc}')

def aw_create(
    domain: str = "auth.activeworlds.com",
    port: int = 6670
) -> c_void_p:
    """
    Creates a bot instance for the specified domain and port.

    Args:
        domain (str): The universe domain. Defaults to "auth.activeworlds.com".
        port (int): The universe port. Defaults to 6670.

    Returns:
        c_void_p: The bot instance.
    """
    return aw_create_resolved(
        address=socket.inet_aton(
            socket.gethostbyname(domain), # Little Endian
        ),
        port=port
    )

def aw_create_resolved(address: bytes, port: int) -> c_void_p:
    """
    Creates a bot instance for the specified address and port.

    Args:
        address (bytes): The address of the universe stored in network byte order.
        port (int): The universe port.

    Raises:
        Exception: If the bot instance could not be created.

    Returns:
        c_void_p: The bot instance.
    """
    instance = c_void_p()
    address = c_ulong(int.from_bytes(address, byteorder='little')) # Little Endian, not network byte order
    SDK.aw_create_resolved.argtypes = [c_ulong, c_int, POINTER(c_void_p)]
    rc = SDK.aw_create_resolved(address, port, instance)

    if rc:
        raise Exception(f"Failed to create bot instance: {rc}")

    return instance

def aw_data(attribute: AttributeEnum, ret_type = c_char) -> Union[bytes, list[bytes]]:
    """
    Gets a data attribute.

    Args:
        attribute (AttributeEnum): The attribute name.
        ret_type (c_char, optional): The return type. Defaults to c_char.

    Raises:
        Exception: If the attribute could not be retrieved.

    Returns:
        Union[bytes, list[bytes]]: The attribute value.
    """
    SDK.aw_data.restype = POINTER(ret_type)
    SDK.aw_data.argtypes = [c_int, POINTER(c_uint)]
    data_length = c_uint()

    data_p = SDK.aw_data(attribute.value, byref(data_length))

    if data_length.value <= 1:
        return data_p
        
    return [data_p[i] for i in range(data_length.value)]

def aw_data_set(attribute: AttributeEnum, value: bytes, ret_type = c_char) -> None:
    """
    Sets a data attribute.

    Args:
        attribute (AttributeEnum): The attribute name.
        value (bytes): The attribute value.
        ret_type (c_char, optional): The data type in c. Defaults to c_char.

    Raises:
        Exception: If the attribute could not be set.
    """
    SDK.aw_data_set.restype = c_int
    SDK.aw_data_set.argtypes = [c_int, POINTER(ret_type), c_uint]

    length = len(value) if value else 0

    rc = SDK.aw_data_set(attribute.value, value, length)

    if rc:
        raise Exception(f"Failed to set data attribute: {rc}")

def aw_delete_all_objects() -> None:
    """
    Deletes all objects.

    Raises:
        Exception: If the objects could not be deleted.
    """    
    SDK.aw_delete_all_objects.restype = c_int
    SDK.aw_delete_all_objects.argtypes = []

    if rc := SDK.aw_delete_all_objects():
        raise Exception(f"Failed to delete all objects: {rc}")

def aw_destroy(instance: c_void_p) -> None:
    """
    Destroys a bot instance.

    Args:
        instance (c_void_p): The bot instance.
    """
    if rc := SDK.aw_destroy(instance):
        raise Exception(f"Failed to destroy bot instance: {rc}")

def aw_enter(world: str) -> None:
    """
    Enters the universe at a specified world.

    Args:
        name (str): The name of the world.

    Raises:
        Exception: If the world could not be entered.
    """
    rc = SDK.aw_enter(world.encode('utf-8'))

    if rc:
        raise Exception(f"Failed to enter universe: {rc}")

def aw_event(event: EventEnum) -> c_void_p:
    """
    Get the event handler for the specified event.

    Args:
        event (EventEnum): The event name.

    Raises:
        Exception: If the event handler could not be retrieved.

    Returns:
        POINTER(c_int): The event handler.
    """
    return SDK.aw_event(event.value)

def aw_event_set(event: EventEnum, handler: AW_CALLBACK) -> None:
    """
    Sets an event handler.

    Args:
        event (Event): The event.
        handler (AW_CALLBACK): The event handler.

    Raises:
        Exception: If the event handler could not be set.
    """
    rc = SDK.aw_event_set(event.value, handler)

    if rc:
        raise Exception(f"Failed to set event handler: {rc}, {event}")

def aw_exit() -> None:
    """
    Exits the world.

    Raises:
        Exception: If the world could not be exited.
    """
    rc = SDK.aw_exit()

    if rc:
        raise Exception(f"Failed to exit world: {rc}")

def aw_float(attribute: AttributeEnum) -> float:
    """
    Gets a float attribute.

    Args:
        attribute (AttributeEnum): The attribute name.

    Raises:
        Exception: If the attribute could not be retrieved.

    Returns:
        float: The attribute value.
    """
    return float(SDK.aw_float(attribute.value))

def aw_float_set(attribute: AttributeEnum, value: float) -> None:
    """
    Sets an initialization attribute.

    Args:
        attribute (AttributeEnum): The attribute name.
        value (float): The attribute value.

    Raises:
        Exception: If the attribute could not be set.
    """
    rc = SDK.aw_float_set(attribute.value, value)

    if rc:
        raise Exception(f"Failed to set initialization attribute: {rc}")

def aw_has_world_right(citizen: int, right: RightsEnum) -> bool:
    """
    Checks if a citizen has a specified world right.

    Args:
        citizen (int): The citizen number.
        right (RightsEnum): The right.

    Returns:
        bool: True if the citizen has the right, False otherwise.
    """    
    return SDK.aw_has_world_right(citizen, right.value)

def aw_has_world_right_all(right: AttributeEnum) -> bool:
    """
    Checks if everyone in the world has a specified world right.

    Args:
        right (AttributeEnum): The right.

    Returns:
        bool: True if everyone in the world has the right, False otherwise.
    """
    return bool(SDK.aw_has_world_right_all(right.value))

def aw_hud_clear(session: int) -> None:
    """
    Clears the HUD for the given session. Will clear HUD for all sessions if session is 0.

    Args:
        session (int): The session number.

    Raises:
        Exception: If the HUD could not be cleared.
    """    
    rc = SDK.aw_hud_clear(session)

    if rc:
        raise Exception(f"Failed to clear HUD: {rc}")

def aw_hud_click(hud_click: data.HudClickData) -> None:
    """
    Simulates a HUD click.

    Args:
        hud_click (data.HudClickData): The HUD click data.

    Raises:
        Exception: If the HUD click could not be simulated.
    """
    aw_int_set(AttributeEnum.AW_HUD_ELEMENT_ID, hud_click.id)
    aw_int_set(AttributeEnum.AW_HUD_CLICK_X, hud_click.x)
    aw_int_set(AttributeEnum.AW_HUD_CLICK_Y, hud_click.y)
    aw_int_set(AttributeEnum.AW_HUD_ELEMENT_CLICK_Z, hud_click.z)

    rc = SDK.aw_hud_click()

    if rc:
        raise Exception(f"Failed to simulate HUD click: {rc}")

def aw_hud_create(hud: data.HudData) -> None:
    """
    Creates a HUD element.

    Args:
        hud (data.HudData): The HUD data.

    Raises:
        Exception: If the HUD element could not be created.
    """
    from .write_data import write_data

    for field in fields(hud):
        write_data(
            AttributeEnum(f"AW_HUD_ELEMENT_{field.upper()}"),
            getattr(hud, field.name)
        )

    rc = SDK.aw_hud_create()

    if rc:
        raise Exception(f"Failed to create HUD element: {rc}")

def aw_hud_destroy(session: int, id: int) -> None:
    """
    Destroys a HUD element.

    Args:
        session (int): The session number. 0 for all sessions.
        id (int): The HUD element ID.
    """
    rc = SDK.aw_hud_destroy(session, id)

    if rc:
        raise Exception(f"Failed to destroy HUD element: {rc}")

def aw_init(build: int) -> None:
    """
    Initializes the Active Worlds Software Development Kit.

    Args:
        build (int): The build number of the SDK.

    Returns:
        int: The result of the initialization.

    Raises:
        Exception: If the initialization fails.

    See:
        http://wiki.activeworlds.com/index.php?title=SDK_Reason_Codes
    """
    rc = SDK.aw_init(build)

    if rc:
        raise Exception(f"Failed to initialize SDK: {rc}")

def aw_instance() -> c_void_p:
    """
    Gets the current instance.

    Raises:
        Exception: If the instance could not be retrieved.
    
    Returns:
        c_void_p: The instance.
    """
    return SDK.aw_instance()

def aw_instance_callback_set(callback: CallBackEnum, handler: c_void_p) -> None:
    """
    Sets an instance callback.

    Args:
        callback (CallBackEnum): The callback event.
        handler (c_void_p): The callback handler.

    Raises:
        Exception: If the callback could not be set.
    """
    rc = SDK.aw_instance_callback_set(callback.value, handler)

    if rc:
        raise Exception(f"Failed to set instance callback: {rc}")

def aw_instance_event_set(event: EventEnum, handler: c_void_p) -> None:
    """
    Sets an instance event.

    Args:
        event (EventEnum): The event.
        handler (c_void_p): The event handler.

    Raises:
        Exception: If the event could not be set.
    """    
    rc = SDK.aw_instance_event_set(event.value, handler)

    if rc:
        raise Exception(f"Failed to set instance event: {rc}")

def aw_instance_set(instance: c_void_p) -> None:
    """
    Sets the bot instance.

    Args:
        instance (c_void_p): The bot instance.

    Raises:
        Exception: If the instance could not be set.
    """
    rc = SDK.aw_instance_set(instance)

    if rc:
        raise Exception(f"Failed to set instance: {rc}")

def aw_int(attribute: AttributeEnum) -> int:
    """
    Gets an integer attribute.

    Args:
        attribute (AttributeEnum): The attribute name.

    Raises:
        Exception: If the attribute could not be retrieved.

    Returns:
        int: The attribute value.
    """
    return int(SDK.aw_int(attribute.value))

def aw_laser_beam(laser_beam: data.LaserBeamData) -> None:
    """
    Creates a laser beam.

    Args:
        laser_beam (data.LaserBeamData): The laser beam data.
    """
    from .write_data import write_data

    for field in fields(laser_beam):
        write_data(
            AttributeEnum(f"AW_LASER_BEAM_{field.upper()}"),
            getattr(laser_beam, field.name)
        )

    rc = SDK.aw_laser_beam()

    if rc:
        raise Exception(f"Failed to create laser beam: {rc}")

def aw_license_add(license_create: data.LicenseCreateData) -> None:
    """
    Adds a world license.

    Args:
        license_create (data.LicenseData): The license data.

    Raises:
        Exception: If the license could not be added.
    """    
    from .write_data import write_data

    for field in fields(license_create):
        write_data(
            AttributeEnum(f"AW_LICENSE_{field.upper()}"),
            getattr(license_create, field.name)
        )

    rc = SDK.aw_license_add()

    if rc:
        raise Exception(f"Failed to add license: {rc}")

def aw_license_attributes(name: str) -> data.LicenseData:
    """
    Gets the world license attributes.

    Args:
        name (str): The license name.

    Raises:
        Exception: If the license attributes could not be retrieved.

    Returns:
        LicenseData: The license attributes.
    """
    from .get_data import get_data

    rc = SDK.aw_license_attributes(name)

    if rc:
        raise Exception(f"Failed to get license attributes: {rc}")

    license_data = data.LicenseData()
    for field in fields(license_data):
        setattr(
            license_data,
            field.name,
            get_data(AttributeEnum(f"AW_LICENSE_{field.upper()}"))
        )

    return license_data

def aw_license_change(license_change: data.LicenseChangeData) -> None:
    """
    Changes a world license.

    Args:
        data (data.LicenseChangeData): The license data.

    Raises:
        Exception: If the license could not be changed.
    """    
    from .write_data import write_data

    for field in fields(license_change):
        write_data(
            AttributeEnum(f"AW_LICENSE_{field.upper()}"),
            getattr(license_change, field.name)
        )
    
    rc = SDK.aw_license_change()
    
    if rc:
        raise Exception(f"Failed to change license: {rc}")

def aw_license_delete(name: str) -> None:
    """
    Deletes a world license.

    Args:
        name (str): The license name.
    """
    rc = SDK.aw_license_delete(name)

    if rc:
        raise Exception(f"Failed to delete license: {rc}")

def aw_license_next() -> data.LicenseData:
    """
    Gets the next world license.

    Raises:
        Exception: If the license could not be retrieved.

    Returns:
        LicenseData: The license data.
    """
    from .get_data import get_data

    rc = SDK.aw_license_next()

    if rc:
        raise Exception(f"Failed to get next license: {rc}")

    license_data = data.LicenseData()
    for field in fields(license_data):
        setattr(
            license_data,
            field.name,
            get_data(AttributeEnum(f"AW_LICENSE_{field.upper()}"))
        )
    
    return license_data

def aw_license_previous() -> data.LicenseData:
    """
    Gets the previous world license.

    Raises:
        Exception: If the license could not be retrieved.

    Returns:
        LicenseData: The license data.
    """
    from .get_data import get_data

    rc = SDK.aw_license_previous()

    if rc:
        raise Exception(f"Failed to get previous license: {rc}")

    license_data = data.LicenseData()
    for field in fields(license_data):
        setattr(
            license_data,
            field.name,
            get_data(AttributeEnum(f"AW_LICENSE_{field.upper()}"))
        )

    return license_data

def aw_login(instance: c_void_p, login: data.LoginData) -> None:
    """
    Logs into the universe.

    Args:
        instance (c_void_p): The bot instance.
        login (data.LoginData): The login data.

    Raises:
        Exception: If the login failed.
    """
    aw_instance_set(instance)

    aw_int_set(AttributeEnum.AW_LOGIN_OWNER, login.citizen)
    aw_string_set(AttributeEnum.AW_LOGIN_PRIVILEGE_PASSWORD, login.password)
    aw_string_set(AttributeEnum.AW_LOGIN_APPLICATION, login.app_name)
    aw_string_set(AttributeEnum.AW_LOGIN_NAME, login.bot_name)
    
    rc = SDK.aw_login()

    if rc:
        raise Exception(f"Failed to login: {rc}")

def aw_mover_links(id: int) -> None:
    """
    Gets the mover links. Triggers the mover links event.

    Args:
        id (int): The mover ID.

    Raises:
        Exception: If the mover links could not be retrieved.
    """    
    rc = SDK.aw_mover_links(id)

    if rc:
        raise Exception(f"Failed to get mover links: {rc}")

def aw_mover_rider_add(id: int, session: int, dist: int, angle: int, y_delta: int, yaw_delta: int, pitch_delta: int) -> None:
    """
    Adds a mover rider. Triggers the mover rider add event.

    Args:
        id (int): The mover ID.
        session (int): The session ID.
        dist (int): Distance in the XZ plane from the origo of the mover object to the rider.
        angle (int): Angle in the XZ plane between the Z axis of the mover object and the rider.
        y_delta (int): Distance along the Y axis from the origo of the mover to the Y coordinate of the rider.
        yaw_delta (int): Yaw of the rider, relative to the yaw of the mover object.
        pitch_delta (int): Pitch of the rider, relative to the pitch of the mover object.

    Raises:
        Exception: If the mover rider could not be added.
    """
    rc = SDK.aw_mover_rider_add(id, session, dist, angle, y_delta, yaw_delta, pitch_delta)

    if rc:
        raise Exception(f"Failed to add mover rider: {rc}")
    rc = SDK.aw_destroy(instance)
def aw_mover_rider_change(id: int, session: int, dist: int, angle: int, y_delta: int, yaw_delta: int, pitch_delta: int) -> None:
    """
    Changes a mover rider. Triggers the mover rider change event.

    Args:
        id (int): The mover ID.
        session (int): The session ID.
        dist (int): Distance in the XZ plane from the origo of the mover object to the rider.
        angle (int): Angle in the XZ plane between the Z axis of the mover object and the rider.
        y_delta (int): Distance along the Y axis from the origo of the mover to the Y coordinate of the rider.
        yaw_delta (int): Yaw of the rider, relative to the yaw of the mover object.
        pitch_delta (int): Pitch of the rider, relative to the pitch of the mover object.

    Raises:
        Exception: If the mover rider could not be changed.
    """
    rc = SDK.aw_mover_rider_change(id, session, dist, angle, y_delta, yaw_delta, pitch_delta)

    if rc:
        raise Exception(f"Failed to change mover rider: {rc}")

def aw_mover_rider_delete(id: int, session: int) -> None:
    """
    Deletes a mover rider. Triggers the mover rider delete event.

    Args:
        id (int): The mover ID.
        session (int): The session ID.

    Raises:
        Exception: If the mover rider could not be deleted.
    """
    rc = SDK.aw_mover_rider_delete(id, session)

    if rc:
        raise Exception(f"Failed to delete mover rider: {rc}")

def aw_mover_set_position(id: int, x: int, y: int, z: int, yaw: int, pitch: int, roll: int) -> None:
    """
    Sets the position of a mover. Triggers the mover set position event.

    Args:
        id (int): The mover ID.
        x (int): X coordinate.
        y (int): Y coordinate.
        z (int): Z coordinate.
        yaw (int): Yaw.
        pitch (int): Pitch.
        roll (int): Roll.

    Raises:
        Exception: If the mover position could not be set.
    """
    rc = SDK.aw_mover_set_position(id, x, y, z, yaw, pitch, roll)

    if rc:
        raise Exception(f"Failed to set mover position: {rc}")

def aw_mover_set_state(id: int, state: int, model_num: int) -> None:
    """
    Sets the state of a mover. Triggers the mover set state event.

    Args:
        id (int): The mover ID.
        state (int): The state.
        model_num (int): The model number.
    
    Raises:
        Exception: If the mover state could not be set.
    """
    rc = SDK.aw_mover_set_state(id, state, model_num)

    if rc:
        raise Exception(f"Failed to set mover state: {rc}")

def aw_noise(session_id: int, sound_file: str) -> None:
    """
    Plays a noise. Triggers the noise event.

    Args:
        session_id (int): The session ID or 0 for all sessions.
        sound_file (str): Absolute url or relative path to the sound file.

    Raises:
        Exception: If the noise could not be played.
    """    
    aw_string_set(AttributeEnum.AW_SOUND_NAME, sound_file)
    rc = SDK.aw_noise(session_id)

    if rc:
        raise Exception(f"Failed to play noise: {rc}")

def aw_object_add(object_create: data.ObjectCreateData) -> data.ObjectCreatedData:
    """
    Creates an object.

    Args:
        object_create (data.ObjectCreateData): The object data.

    Returns:
        ObjectCreatedData: The created object data.
    """
    from .get_data import get_data
    from .write_data import write_data

    for field in fields(object_create):
        value = getattr(object_create, field.name, None)
        attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
        write_data(attr, value)

    rc = SDK.aw_object_add()

    if rc:
        raise Exception(f"Failed to create object: {rc}")

    ret = data.ObjectCreatedData()
    for field in fields(ret):
        prepend = 'AW_OBJECT_'
        if 'CELL' in field.name.upper():
            prepend = 'AW_'
        attr = getattr(AttributeEnum, f'{prepend}{field.name.upper()}')
        object_create = get_data(attr)

        if object_create:
            setattr(ret, field.name, object_create)

    return ret

def aw_object_bump(object_bump: data.ObjectBumpData) -> Tuple[int, int]:
    """
    Simulates a bump on an object.

    Args:
        object_bump (data.ObjectBumpData): The object data.

    Raises:
        Exception: If the object could not be bumped.

    Returns:
        Tuple[int, int]: Object sync, and session ID.
    """    
    from .get_data import get_data
    from .write_data import write_data

    for field in fields(object_bump):
        value = getattr(object_bump, field.name, None)
        attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
        write_data(attr, value)
    
    rc = SDK.aw_object_bump()

    if rc:
        raise Exception(f"Failed to bump object: {rc}")

    return get_data(AttributeEnum.AW_OBJECT_SYNC), get_data(AttributeEnum.AW_OBJECT_SESSION_TO)

def aw_object_change(object_change: data.ObjectChangeData) -> None:
    """
    Changes an object.

    Args:
        object_change (data.ObjectChangeData): The object data.

    Raises:
        Exception: If the object could not be changed.
        Exception: If the change data has an unsupported type.
    """
    from .write_data import write_data

    for field in fields(object_change):
        value = getattr(object_change, field.name, None)
        attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
        write_data(attr, value)

    rc = SDK.aw_object_change()

    if rc:
        raise Exception(f"Failed to change object: {rc}")

def aw_object_click(object_click: data.ObjectClickData) -> data.ObjectClickedData:
    """
    Simulates a click on an object.

    Args:
        object_click (data.ObjectClickData): The object data.

    Returns:
        data.ObjectClickedData: The clicked object data.
    """    
    from .get_data import get_data
    from .write_data import write_data

    for field in fields(object_click):
        value = getattr(object_click, field.name, None)
        attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
        write_data(attr, value)

    rc = SDK.aw_object_click()

    if rc:
        raise Exception(f"Failed to click object: {rc}")

    ret = data.ObjectClickedData()
    for field in fields(ret):
        prepend = 'AW_OBJECT_'
        if 'CELL' in field.name.upper():
            prepend = 'AW_'
        attr = getattr(AttributeEnum, f'{prepend}{field.name.upper()}')
        object_click = get_data(attr)

        if object_click:
            setattr(ret, field.name, object_click)

    return ret

def aw_object_delete(object_delete: data.ObjectDeleteData) -> None:
    """
    Deletes an object.

    Args:
        object_delete (data.ObjectDeleteData): The object data.

    Raises:
        Exception: If the object could not be deleted.
    """
    from .write_data import write_data

    for field in fields(object_delete):
        value = getattr(object_delete, field.name, None)
        attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
        if value:
            write_data(attr, value)

    rc = SDK.aw_object_delete()

    if rc:
        raise Exception(f"Failed to delete object: {rc}")

def aw_object_load(object_load: data.ObjectLoadData) -> data.ObjectLoadedData:
    """
    Loads an object. Requires eminient domain due to the fact that it overrides owner and timestamp.

    Args:
        object_load (data.ObjectLoadData): The object data.

    Raises:
        Exception: If the object could not be loaded.

    Returns:
        data.ObjectLoadedData: The loaded object data.
    """
    from .get_data import get_data
    from .write_data import write_data

    for field in fields(object_load):
        value = getattr(object_load, field.name, None)
        if 'cell' not in field.name.lower():
            attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
            write_data(attr, value)
        else:
            attr = getattr(AttributeEnum, f'AW_{field.name.upper()}')
            write_data(attr, value)

    rc = SDK.aw_object_load()
    
    if rc:
        raise Exception(f"Failed to load object: {rc}")

    ret = data.ObjectLoadedData()
    for field in fields(ret):
        prepend = 'AW_OBJECT_'
        if 'CELL' in field.name.upper():
            prepend = 'AW_'
        attr = getattr(AttributeEnum, f'{prepend}{field.name.upper()}')
        object_load = get_data(attr)

        if object_load:
            setattr(ret, field.name, object_load)

    return ret

def aw_object_query(object_query: Union[data.ObjectQueryData, int]) -> data.ObjectQueriedData:
    """
    Queries an object.

    Args:
        object_query (Union[data.ObjectQueryData, int]): The object data or object ID.

    Returns:
        data.ObjectQueriedData: The queried object data.
    """    
    from .get_data import get_data
    from .write_data import write_data

    if isinstance(object_query, int):
        write_data(AttributeEnum.AW_OBJECT_ID, object_query)
    else:
        for field in fields(object_query):
            value = getattr(object_query, field.name, None)
            attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
            write_data(attr, value)
    
    rc = SDK.aw_object_query()

    if rc:
        raise Exception(f"Failed to query object: {rc}")

    ret = data.ObjectQueriedData()
    for field in fields(ret):
        attr = getattr(AttributeEnum, f'AW_OBJECT_{field.name.upper()}')
        object_query = get_data(attr)

        if object_query:
            setattr(ret, field.name, object_query)

    return ret

def aw_object_select(*args: typing.Any) -> typing.Any:
    return SDK.aw_object_select(*args)

def aw_query(x_sector: int, z_sector: int, sequence3_x_3: List[List[int]]) -> None:
    """
    Queries the world using longitude and latitude.

    Args:
        x_sector (int): The longitude sector.
        z_sector (int): The latitude sector.
        sequence3_x_3 (List[List[int]]): The sequence of 3 x 3 cells.

    Raises:
        Exception: If the query failed.
        Exception: If the sequence is invalid.
    """
    if len(sequence3_x_3) != 3:
        raise Exception("The sequence must be 3 x 3.")

    for row in sequence3_x_3:
        if len(row) != 3:
            raise Exception("The sequence must be 3 x 3.")
    
    sequence = (c_int * 9)(*[x for row in sequence3_x_3 for x in row])
    SDK.aw_query.argtypes = [c_int, c_int, (c_int * 9)]
    SDK.aw_query.restype = c_int
    rc = SDK.aw_query(x_sector, z_sector, sequence)

    if rc:
        raise Exception(f"Failed to query: {rc}")

def aw_say(message: str) -> None:
    """
    Sends a message to the universe.

    Args:
        message (str): The message to send.

    Raises:
        Exception: If the message could not be sent.
    """
    rc = SDK.aw_say(message.encode('utf-8'))

    if rc:
        raise Exception(f"Failed to send message: {rc}")

def aw_sector_from_cell(cell: int) -> int:
    """
    Get the sector that a cell is located in.

    Args:
        cell (int): The cell.
    """
    SDK.aw_sector_from_cell.argtypes = [c_int]
    SDK.aw_sector_from_cell.restype = c_int
    
    return SDK.aw_sector_from_cell(cell)

def aw_server_admin(domain: str, port: int, password: str, instance: c_void_p) -> Tuple[int, int]:
    """
    Connects to a world server.

    Args:
        domain (str): The domain.
        port (int): The port.
        password (str): The password.
        instance (c_void_p): The instance.

    Raises:
        Exception: If the connection failed.

    Returns:
        Tuple[int, int]: Server build, build number.
    """
    SDK.aw_server_admin.argtypes = [c_char_p, c_int, c_char_p, c_void_p]
    SDK.aw_server_admin.restype = c_int

    rc = SDK.aw_server_admin(domain.encode('utf-8'), port, password.encode('utf-8'), instance)

    if rc:
        raise Exception(f"Failed to connect: {rc}")

def aw_server_world_add(server: data.ServerData) -> data.ServerReturnData:
    """
    Add a world to the universe.

    Args:
        server (ServerCreateData): The world data.

    Returns:
        ServerReturnData: The created world data.
    """
    from .get_data import get_data
    from .write_data import write_data

    for field in fields(server):
        value = getattr(server, field.name, None)
        attr = getattr(AttributeEnum, f'AW_SERVER_{field.name.upper()}')
        write_data(attr, value)

    rc = SDK.aw_server_world_add()

    if rc:
        raise Exception(f"Failed to create world: {rc}")

    ret = data.ServerReturnData()
    for field in fields(ret):
        attr = getattr(AttributeEnum, f'AW_SERVER_{field.name.upper()}')
        attr_data = get_data(attr)

        if attr_data:
            setattr(ret, field.name, attr_data)

    return ret

def aw_server_world_change(server: data.ServerData) -> data.ServerReturnData:
    """
    Change a world.

    Args:
        server (ServerChangeData): The world data.

    Returns:
        ServerReturnData: The changed world data.
    """
    from .get_data import get_data
    from .write_data import write_data

    for field in fields(server):
        value = getattr(server, field.name, None)
        attr = getattr(AttributeEnum, f'AW_SERVER_{field.name.upper()}')
        write_data(attr, value)

    rc = SDK.aw_server_world_change()

    if rc:
        raise Exception(f"Failed to create world: {rc}")

    ret = data.ServerReturnData()
    for field in fields(ret):
        attr = getattr(AttributeEnum, f'AW_SERVER_{field.name.upper()}')
        attr_data = get_data(attr)

        if attr_data:
            setattr(ret, field.name, attr_data)

    return ret

def aw_server_world_delete(id: int) -> data.ServerReturnData:
    """
    Delete a world.

    Args:
        id (int): The world ID.

    Returns:
        ServerReturnData: The deleted world data.
    """
    from .get_data import get_data

    rc = SDK.aw_server_world_delete(id)

    if rc:
        raise Exception(f"Failed to delete world: {rc}")

    ret = data.ServerReturnData()
    for field in fields(ret):
        attr = getattr(AttributeEnum, f'AW_SERVER_{field.name.upper()}')
        attr_data = get_data(attr)

        if attr_data:
            setattr(ret, field.name, attr_data)

    return ret

def aw_server_world_instance_add(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_instance_add(*args)

def aw_server_world_instance_delete(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_instance_delete(*args)

def aw_server_world_instance_set(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_instance_set(*args)

def aw_server_world_list(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_list(*args)

def aw_server_world_set(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_set(*args)

def aw_server_world_start(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_start(*args)

def aw_server_world_stop(*args: typing.Any) -> typing.Any:
    return SDK.aw_server_world_stop(*args)

def aw_session(*args: typing.Any) -> typing.Any:
    return SDK.aw_session(*args)

def aw_state_change(instance: c_void_p, state_change: data.StateChangeData) -> None:
    """
    Informs the world server of your avatar's current state.

    Args:
        instance (c_void_p): The bot instance.
        state_change (data.StateChangeData): The state change data.

    Raises:
        Exception: If the state change failed.
    """
    aw_instance_set(instance)
    
    for field in fields(state_change):
        value = getattr(state_change, field.name, None)
        attr = getattr(AttributeEnum, f'AW_MY_{field.name.upper()}')
        if value:
            aw_int_set(attr, value)

    rc = SDK.aw_state_change()

    if rc:
        raise Exception(f"Failed to check state change: {rc}")

def aw_string(attribute: AttributeEnum) -> str:
    """
    Gets a string attribute.

    Args:
        attribute (AttributeEnum): The attribute name.

    Raises:
        Exception: If the attribute could not be retrieved.

    Returns:
        str: The attribute value.
    """
    SDK.aw_string.restype = c_char_p
    return SDK.aw_string(attribute.value).decode('utf-8')

def aw_string_from_unicode(*args: typing.Any) -> typing.Any:
    return SDK.aw_string_from_unicode(*args)

def aw_string_set_MBCS_codepage(*args: typing.Any) -> typing.Any:
    return SDK.aw_string_set_MBCS_codepage(*args)

def aw_string_to_unicode(*args: typing.Any) -> typing.Any:
    return SDK.aw_string_to_unicode(*args)

def aw_teleport(*args: typing.Any) -> typing.Any:
    return SDK.aw_teleport(*args)

def aw_term() -> None:
    """
    Terminates the Active Worlds Software Development Kit.
    """    
    SDK.aw_term()

def aw_terrain_delete_all(*args: typing.Any) -> typing.Any:
    return SDK.aw_terrain_delete_all(*args)

def aw_terrain_load_node(*args: typing.Any) -> typing.Any:
    return SDK.aw_terrain_load_node(*args)

def aw_terrain_next() -> bool:
    """
    Gets the next terrain node.

    Raises:
        Exception: If an error occured.

    Returns:
        bool: True if completed, False if not.
    """
    aw_int_set(
        AttributeEnum.AW_TERRAIN_VERSION_NEEDED,
        2
    )

    SDK.aw_terrain_next.restype = c_int
    rc = SDK.aw_terrain_next()

    if rc:
        raise Exception(f"Failed to get next terrain: {rc}")

    return aw_bool(AttributeEnum.AW_TERRAIN_COMPLETE)

def aw_terrain_query(page_x: int, page_z: int, sequence: int) -> bool:
    """
    Queries the terrain for the specified page.

    Args:
        page_x (int): The page's X coordinate.
        page_z (int): The page's Z coordinate.
        sequence (int): The sequence number.

    Raises:
        Exception: If the terrain query failed.

    Returns:
        bool: True if the terrain query has completed, False otherwise.
    """
    SDK.aw_terrain_query.argtypes = [c_int, c_int, c_ulong]
    SDK.aw_terrain_query.restype = c_int
    
    rc = SDK.aw_terrain_query(page_x, page_z, sequence)

    if rc:
        raise Exception(f"Failed to query terrain: {rc}")

    return aw_bool(AttributeEnum.AW_TERRAIN_COMPLETE)

def aw_terrain_set(*args: typing.Any) -> typing.Any:
    return SDK.aw_terrain_set(*args)

def aw_tick() -> int:
    """
    Number of ticks since the number SDK was initialized.

    Returns:
        int: The number of ticks.
    """
    return SDK.aw_tick()

def aw_toolbar_click(*args: typing.Any) -> typing.Any:
    return SDK.aw_toolbar_click(*args)

def aw_traffic_count(*args: typing.Any) -> typing.Any:
    return SDK.aw_traffic_count(*args)

def aw_universe_attributes_change(*args: typing.Any) -> typing.Any:
    return SDK.aw_universe_attributes_change(*args)

def aw_universe_ejection_add(*args: typing.Any) -> typing.Any:
    return SDK.aw_universe_ejection_add(*args)

def aw_universe_ejection_delete(*args: typing.Any) -> typing.Any:
    return SDK.aw_universe_ejection_delete(*args)

def aw_universe_ejection_lookup(*args: typing.Any) -> typing.Any:
    return SDK.aw_universe_ejection_lookup(*args)

def aw_universe_ejection_next(*args: typing.Any) -> typing.Any:
    return SDK.aw_universe_ejection_next(*args)

def aw_universe_ejection_previous(*args: typing.Any) -> typing.Any:
    return SDK.aw_universe_ejection_previous(*args)

def aw_unzip(*args: typing.Any) -> typing.Any:
    return SDK.aw_unzip(*args)

def aw_url_click(url: str) -> None:
    """
    Simulates a url click.

    Args:
        url (str): The url to click.

    Raises:
        Exception: If the url click failed.
    """
    rc = SDK.aw_url_click(url)

    if rc:
        raise Exception(f"Failed to click url: {rc}")

def aw_url_send(session_id: int, url: str, target: str, post: bool = False, target_3d: bool = False)-> None:
    """
    Sends a url to the specific session with a target frame.

    Args:
        session_id (int): The session id.
        url (str): The url to send.
        target (str): The target frame.
        post (bool): True if the url is a post, False otherwise.
        target_3d (bool): True if the target is a 3D frame, False otherwise.

    Raises:
        Exception: If the url send failed.
    """
    aw_bool_set(AttributeEnum.AW_URL_POST, post)
    aw_bool_set(AttributeEnum.AW_URL_TARGET_3D, target_3d)
    
    rc = SDK.aw_url_send(session_id, url, target)

    if rc:
        raise Exception(f"Failed to send url: {rc}")

def aw_user_data(*args: typing.Any) -> typing.Any:
    return SDK.aw_user_data(*args)

def aw_user_data_set(*args: typing.Any) -> typing.Any:
    return SDK.aw_user_data_set(*args)

def aw_user_list(*args: typing.Any) -> typing.Any:
    return SDK.aw_user_list(*args)

def aw_wait(milliseconds: int = -1) -> None:
    """
    Waits for a specified amount of time.
    Negative 1 is infinite.

    Args:
        milliseconds (int, optional): The amount of time to wait in milliseconds. Defaults to -1.

    Raises:
        Exception: If the wait failed.
    """    
    rc = SDK.aw_wait(milliseconds)

    if rc:
        raise Exception(f"Failed to wait: {rc}")

def aw_whisper(session_id: int, message: str) -> None:
    """
    Whispers a message to a specified session.

    Args:
        session_id (int): The session to whisper to.
        message (str): The message to whisper.
    """
    rc = SDK.aw_whisper(session_id, message.encode('utf-8'))

    if rc:
        raise Exception(f"Failed to send whisper: {rc}")

def aw_world_attribute_get(attribute: int) -> Union[bool, str]:
    """
    Gets a world attribute.

    Args:
        attribute (int): The attribute to get. These attributes aren't documented.

    Raises:
        Exception: If the attribute could not be retrieved.

    Returns:
        Union[bool, str]: Read Only, The attribute value.
    """    
    SDK.aw_world_attribute_get.argtypes = [c_int, POINTER(c_int), c_char_p]

    read_only = c_int()
    value = c_char_p()
    rc = SDK.aw_world_attribute_get(attribute, read_only, value.encode('utf-8'))

    if rc:
        raise Exception(f"Failed to get world attribute: {rc}")

    return bool(read_only), value.decode('utf-8')

def aw_world_attribute_set(attribute: int, value: str) -> None:
    """
    Sets a world attribute.
    
    Args:
        attribute (int): The attribute to set. These attributes aren't documented.
        value (str): The attribute value.
    """
    rc = SDK.aw_world_attribute_set(attribute, value.encode('utf-8'))

    if rc:
        raise Exception(f"Failed to set world attribute: {rc}")

def aw_world_attributes_change(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_attributes_change(*args)

def aw_world_attributes_reset(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_attributes_reset(*args)

def aw_world_attributes_send(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_attributes_send(*args)

def aw_world_cav_change(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_cav_change(*args)

def aw_world_cav_delete(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_cav_delete(*args)

def aw_world_cav_request(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_cav_request(*args)

def aw_world_eject(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_eject(*args)

def aw_world_ejection_add(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_ejection_add(*args)

def aw_world_ejection_delete(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_ejection_delete(*args)

def aw_world_ejection_lookup(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_ejection_lookup(*args)

def aw_world_ejection_next(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_ejection_next(*args)

def aw_world_ejection_previous(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_ejection_previous(*args)

def aw_world_instance_get(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_instance_get(*args)

def aw_world_instance_set(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_instance_set(*args)

def aw_world_list(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_list(*args)

def aw_world_reload_registry(*args: typing.Any) -> typing.Any:
    return SDK.aw_world_reload_registry(*args)

def aw_zip(*args: typing.Any) -> typing.Any:
    return SDK.aw_zip(*args)
