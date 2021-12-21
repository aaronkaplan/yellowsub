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

    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)
        # Retrieving configuration
        config = self.config
        print(config)
        try:
            self.path = config["parameters"]["path"]
            self.delete_files = config["parameters"]["delete_files"]
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
            try:
                makedirs(self.path + "/" + self.PROCESSED_FOLDER)
            except PermissionError:
                raise RuntimeError("could not instantiate FileCollector. Reason: could not create processed folder.")

    def process(self, channel=None, method=None, properties=None, msg: dict = Dict[Any, Any]) -> None:
        # Initializing finished variable to false as we just started
        finished = False
        # Initializing file list to empty list
        files = []

        print("RUNNING THE file collector...")
        # Processing
        while not finished:
            # Getting updated version of folder content
            files = listdir(self.path)
            # Switching finished flag, that way if there is only folders or files ending with processing extention
            # while loop will auto close
            finished = True

            # Looking at all files
            for f in files:
                filepath = self.path + "/" + f
                # Only handles files that do not ends with the processing extension
                if path.isfile(filepath) and not f.endswith(self.PROCESSING_EXT):
                    # We are still processing files, so maybe there are more let's do the loop another time
                    finished = False

                    # Rename file with processing extension
                    try:
                        rename(filepath, filepath + self.PROCESSING_EXT)
                    except PermissionError:
                        self.logger.error("could not rename file {} with processing extension. Exiting".format(filepath))
                        # As we could not rename the file there is no way for us to handle further processing, let's
                        # quit here
                        finished = True
                        break
                    except FileNotFoundError:
                        # Maybe we were in a race condition here, so simply log it as info and continue
                        self.logger.info("could not rename file {}. Race condition?".format(filepath))
                        break

                    # Try to open the file
                    fd = open(filepath + self.PROCESSING_EXT, 'rb')

                    # Start building a new message
                    msg = {
                        "format": "raw",
                        "version": 1,
                        "type": "raw",
                        "meta": {
                            "uuid": str(uuid.uuid4())
                        }
                    }

                    # Read content of file and convert it as base64
                    base64_data = str(base64.encodebytes(fd.read()))
                    fd.close()
                    # Add content of file to payload of msg
                    msg["payload"] = {"raw": base64_data}

                    print(f"msg = {msg}")
                    # If option to delete file is set to true then delete the file
                    if self.delete_files:
                        remove(filepath + self.PROCESSING_EXT)
                    else:
                        replace(filepath + self.PROCESSING_EXT,
                                self.path + "/" + self.PROCESSED_FOLDER + "/" + f)

                    # Send message
                    self.producer.produce(msg=msg, routing_key="")

                    # We have processed a file so let's exit the for loop an update directory listing
                    break


PROCESSOR=FileCollector

