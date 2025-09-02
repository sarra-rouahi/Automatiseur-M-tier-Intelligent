'''''
from trigemail import EmailReceivedTrigger
from classifier import EmailClassifierAction
from ocr  import OCRImageAction
from calender import CalendarAddEventAction

NODE_REGISTRY = {
    "email_received_trigger": EmailReceivedTrigger(),
    "email_classifier_action": EmailClassifierAction(),
    "ocr_image_action": OCRImageAction(),
    "calendar_add_event": CalendarAddEventAction(),
}
'''
# registry.py
from backend.base import BaseNode

NODE_REGISTRY = {}

def register_nodes():
    from trigemail import EmailReceivedTrigger
    from classifier import EmailClassifierAction
    from ocr import OCRImageAction
    from backend.calender_node import CalendarAddEventAction

    NODE_REGISTRY.update({
        "email_received_trigger": EmailReceivedTrigger(),
        "email_classifier_action": EmailClassifierAction(),
        "ocr_image_action": OCRImageAction(),
        "calendar_add_event": CalendarAddEventAction(),
    })

register_nodes()

