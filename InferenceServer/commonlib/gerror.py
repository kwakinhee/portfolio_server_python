from commonlib.util.genum import GERROR_CODE
import sys, traceback


class GError(Exception):
    def __init__(self, message: str, gErrCode: GERROR_CODE, extra=None):

        if not isinstance(gErrCode, GERROR_CODE):
            msg = 'Error code passed in the error_code param must be of type {}'
            raise GError(
                msg.format(GERROR_CODE.ERR_INCORRECT_ERRCODE),
                GERROR_CODE.ERR_INCORRECT_ERRCODE
            )

        self.message = message
        self.gcode = gErrCode.value[0]
        self.extra = extra

        # self.execInfo = sys.exc_info()
        # self.traceback = traceback.format_exc()
