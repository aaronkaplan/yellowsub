"""
File output processor
"""
from lib.processor.output import OutputProcessor
from os import path, makedirs
from typing import Dict, Any
from datetime import datetime
import json


class FileOutput(OutputProcessor):

    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)
        # Retrieving configuration
        config = self.config
        try:
            self.path = config["parameters"]["path"]
        except KeyError as e:
            raise RuntimeError("could not load config for FileOutput Reason: {}".format(str(e)))
        # If path does not exist
        if not path.exists(self.path):
            # Try to create it
            try:
                makedirs(self.path)
            except PermissionError:
                raise RuntimeError("could not instantiate FileOutput. Reason: path does not exist and could not be created.")
        # If path exist
        else:
            # Check that it is a folder
            if not path.isdir(self.path):
                raise RuntimeError(
                    "could not instantiate FileOutput. Reason: path exists and is not a folder.")

    def process(self, channel=None, method=None, properties=None, msg: dict = Dict[Any, Any]) -> None:
        # Retrieving needed data and creating timestamp
        payload = msg['payload']
        uuid = msg['meta']['uuid']
        now = datetime.now()
        # Building filename and filepath
        filename = now.strftime("%Y-%m-%dT%H:%M:%S") + "_" + uuid + ".json"
        filepath = self.path + "/" + filename
        # Trying to open the file to write its content
        try:
            fd = open(filepath, 'w')
        except PermissionError:
            self.logger.error("could not open file {} in write mode. Exiting.".format(filepath))
            return
        # Writing content to file
        self.logger.info(f"Sending data to file {filepath}")
        json.dump(payload, fd)
        fd.close()
        self.consumer.ack(method)


PROCESSOR=FileOutput
