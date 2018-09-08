from itsdangerous import URLSafeSerializer

def sign(value):
    if not value:
        return None

    serializer = URLSafeSerializer('my-secret-key', salt='atato')

    signed = serializer.dumps(value)

    return signed

def unsign(signed):
    if not signed:
        return None

    serializer = URLSafeSerializer('my-secret-key', salt='atato')

    unsigned = serializer.loads(signed)

    return unsigned