from rest_framework import status
from rest_framework.response import Response


class CREATED(Response):
    def __init__(self):
        super(CREATED, self).__init__( status = status.HTTP_201_CREATED)

class NO_CONTENT(Response):
    def __init__(self):
        super(NO_CONTENT, self).__init__(status = status.HTTP_204_NO_CONTENT)

class NOT_FOUND(Response):
    def __init__(self, msg = 'Not found'):
        super(NOT_FOUND, self).__init__(msg, status = status.HTTP_404_NOT_FOUND)


class BAD_REQUEST(Response):
    def __init__(self, data):
        super(BAD_REQUEST, self).__init__(data, status = status.HTTP_400_BAD_REQUEST)

class INTERNAL_SERVER_ERROR(Response):
    def __init__(self, msg):
        super(INTERNAL_SERVER_ERROR, self).__init__(f'{msg}. Please try again later.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OK(Response):
    def __init__(self, data = None):
        super(OK, self).__init__(data, status = status.HTTP_200_OK)

class FORBIDDEN(Response):
    def __init__(self):
        super(FORBIDDEN, self).__init__('Oh no, You can\'t touch this though!', status = status.HTTP_403_FORBIDDEN)
