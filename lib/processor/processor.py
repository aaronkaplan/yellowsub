"""Processor - a subclass of Abstract Processor."""
import json

from lib.processor.abstractProcessor import AbstractProcessor
from lib.dataformat import DataFormat


class Processor:
    def __init__(self, id: str, n: int = 1):
        super().__init__(id, n)
        
    def validate(self, msg: bytes) -> bool:
        return super().validate(msg)
    
    def process(self, channel=None, method=None, properties=None, msg: bytes = None):
        return super().process(channel, method, properties, msg)
    
    def on_message(self, msg: bytes):
        super().on_message(msg)
        
        
class JSONProcessor(Processor):
    """This processor can validate JSON message (see dataformat.py)"""
    
    def validate(self, msg:bytes) -> bool:
       return False # XXX FIXME 
