import uuid


def generate_short_uuid():
    return uuid.uuid4().hex[:4]
