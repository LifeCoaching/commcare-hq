from corehq.apps.telerivet.models import TelerivetBackend, IncomingRequest
from corehq.apps.sms.api import incoming as incoming_sms
from corehq.apps.sms.util import strip_plus
from corehq.apps.ivr.api import incoming as incoming_ivr
from celery.task import task
from dimagi.utils.logging import notify_exception
from django.conf import settings

EVENT_INCOMING = "incoming_message"
MESSAGE_TYPE_SMS = "sms"
MESSAGE_TYPE_MMS = "mms"
MESSAGE_TYPE_USSD = "ussd"
MESSAGE_TYPE_CALL = "call"

CELERY_QUEUE = ("sms_queue" if settings.SMS_QUEUE_ENABLED else
    settings.CELERY_MAIN_QUEUE)

@task(queue=CELERY_QUEUE)
def process_incoming_message(*args, **kwargs):
    try:
        log = IncomingRequest(
            event=kwargs["event"],
            message_id=kwargs["message_id"],
            message_type=kwargs["message_type"],
            content=kwargs["content"],
            from_number=kwargs["from_number"],
            from_number_e164=kwargs["from_number_e164"],
            to_number=kwargs["to_number"],
            time_created=kwargs["time_created"],
            time_sent=kwargs["time_sent"],
            contact_id=kwargs["contact_id"],
            phone_id=kwargs["phone_id"],
            service_id=kwargs["service_id"],
            project_id=kwargs["project_id"],
            secret=kwargs["secret"],
        )
        log.save()
    except Exception as e:
        notify_exception(None, "Could not save Telerivet log entry")
        pass

    backend = TelerivetBackend.by_webhook_secret(kwargs["secret"])
    if backend is None:
        # Ignore the message if the webhook secret is not recognized
        return

    from_number = strip_plus(kwargs["from_number"])
    if backend.country_code:
        if not from_number.startswith(backend.country_code):
            from_number = "%s%s" % (backend.country_code, from_number)

    if kwargs["event"] == EVENT_INCOMING:
        if kwargs["message_type"] == MESSAGE_TYPE_SMS:
            incoming_sms(from_number, kwargs["content"], TelerivetBackend.get_api_id())
        elif kwargs["message_type"] == MESSAGE_TYPE_CALL:
            incoming_ivr(from_number, None,
                "TELERIVET-%s" % kwargs["message_id"], None)

