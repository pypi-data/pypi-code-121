import attr


def make_item(data):
    return Item(code=data["code"], id=data["id"], name=data["name"])


def make_component_type(data):
    return ComponentType(
        name=data["name"],
        code=data["code"],
        itemList=list(map(make_item, data["itemList"])),
    )


def make_contacts(data):
    return Contact(
        email=data.get("email"), phone=data.get("phone"), web=data.get("web")
    )


def make_address(data):
    return Address(
        building=data.get("building"),
        city=data.get("city"),
        state=data.get("state"),
        street=data.get("street"),
        zipCode=data.get("zipCode"),
    )


def make_institution(data):
    return Institution(
        address=make_address(data["address"]),
        code=data["code"],
        componentType=list(map(make_component_type, data["componentType"])),
        contacts=make_contacts(data["contacts"]),
        id=data["id"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        name=data["name"],
        supervisor=data["supervisor"],
    )


def make_institution_list(data):
    return InstitutionList(institutions=list(map(make_institution, data)))


@attr.s
class Item(object):
    code = attr.ib()
    id = attr.ib()
    name = attr.ib()


@attr.s
class ComponentType(object):
    code = attr.ib()
    itemList = attr.ib()
    name = attr.ib()


@attr.s
class Contact(object):
    email = attr.ib()
    phone = attr.ib()
    web = attr.ib()


@attr.s
class Address(object):
    building = attr.ib()
    city = attr.ib()
    state = attr.ib()
    street = attr.ib()
    zipCode = attr.ib()


@attr.s
class Institution(object):
    address = attr.ib()
    code = attr.ib()
    componentType = attr.ib()
    contacts = attr.ib()
    id = attr.ib()
    latitude = attr.ib()
    longitude = attr.ib()
    name = attr.ib()
    supervisor = attr.ib()


@attr.s
class InstitutionList(object):
    institutions = attr.ib(type=list)
