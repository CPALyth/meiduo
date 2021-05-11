from .yuntongxun.ccp_sms import CCP
from verifications import constants
from celery_tasks.main import celery_app

@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
    return send_ret

