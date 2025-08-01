from enum import Enum


class PAYLOAD_FLAG(Enum):
    NONE = 0,
    ENCRYPT = 1,
    COMPRESS = 2,
    BINARY = 3,
    LOGOUT = 4,


class GERROR_CODE(Enum):
    OK = 0,

    # critical error.
    UNKNOWN_PACKET_TYPE = 1,

    # non critical error.
    # system
    ERR_INCORRECT_ERRCODE = 9999,
    NON_FATAL_ERROR_MARK = 10000,
    INTERNAL_ERROR = 10001,
    INVALID_PARAMETER = 10002,
    CLIENT_NOT_FOUND = 10003,

    # auth
    INVAILD_ACCESS_TOKEN = 10004,
    INVAILD_CLIENT_TOKEN = 10005,
    DUPLICATE_LOGIN = 10006,
    ALREADY_LOGOUT = 10007,

    # logic
    ALREADY_HAS_SAME_ACTION_STATE = 11000,
    DUPLICATE_ACTION_TYPE = 11001,

    # /fetch configError
    INVALID_PATH_TOKEN = 12000,
    CONFIG_NOT_EXIST = 12001
