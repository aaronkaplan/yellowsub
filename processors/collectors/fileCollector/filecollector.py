"""
File Collector

A file collector needs in its config a directory where ich should search for new files.
A file collector then periodically checks the directory for unprocessed files.
It will then use the Maildir convention of (unix) mv(1) renaming the file:

   <filename.csv> ---> <filename.csv.processing>
   ... process it
   when finished, send the file to <filename.csv> to the subdir "processed/".

Example:

```bash
directory = /tmp/logs/
ls -al $directory
/tmp/logs/1.csv
/tmp/logs/2.csv
/tmp/logs/3.csv
/tmp/logs/processed/
```
# now we process it , after processing it looks like:
ls -al $directory
/tmp/logs/processed/1.csv
/tmp/logs/processed/2.csv
/tmp/logs/processed/3.csv


The output of a file collector

Usual flow:

filecollector --> parser --> process/filter/enrich --> fileOutput (prints in the way the output needs it)

advanced flow:

filecollector -> parser+validator -->  process/filter/enrich --> translator (do different internal payload) -> validator -> processing  ->output.


"""
from lib.processor.collector import Collector
from typing import Dict, Any
from os import path, makedirs, listdir, remove, replace, rename
import uuid
import base64

class FileCollector(Collector):

    PROCESSED_FOLDER = "processed"
    PROCESSING_EXT = ".processing"

    def __init__(self, processor_id: str, n: int = 1):
        super().__init__(processor_id, n)
        # Retrieving configuration
        config = self.config
        try:
            self.path = config["processors"][self.__class__.__name__]["path"]
            self.delete_files = config["processors"][self.__class__.__name__]["delete_files"]
        except KeyError as e:
            raise RuntimeError("could not load config for FileCollector Reason: {}".format(str(e)))
        # Checking folder exists
        if not path.exists(self.path) or not path.isdir(self.path):
            raise RuntimeError("could not instantiate FileCollector. Reason: path does not exist or is not a folder.")
        # Checking value of delete_files is boolean
        if not isinstance(self.delete_files, bool):
            raise RuntimeError("could not instantiate FileCollector. Reason: delete_files is not a boolean.")
        # If delete_files is false then create processed folder
        if not self.delete_files and not path.exists(self.path + "/" + self.PROCESSED_FOLDER):
            makedirs(self.path + "/" + self.PROCESSED_FOLDER)

    def process(self, channel=None, method=None, properties=None, msg: dict = Dict[Any, Any]) -> None:
        # Check content of folder
        for f in listdir(self.path):
            # Only process files
            if path.isfile(f):
                # Start building a new message
                msg = {
                    "format": "raw",
                    "version": 1,
                    "type": "raw",
                    "meta": {
                        "uuid": uuid.uuid4(),
                    },
                }
                # Rename file to .processing
                rename(f, f + self.PROCESSING_EXT)
                # Read content of file and convert it as base64
                fd = open(f + self.PROCESSING_EXT, "rb")
                base64_data = base64.encodebytes(fd.read())
                fd.close()
                # Add content of file to payload of msg
                msg["payload"] = {"raw": base64_data}
                # If option to delete file is set to true then delete the file
                if self.delete_files:
                    remove(f + self.PROCESSING_EXT)
                else:
                    replace(f + self.PROCESSING_EXT, self.path + "/" + self.PROCESSED_FOLDER + "/" + path.basename(f))

                # Send message
                self.producer.produce(msg=msg, routing_key="")