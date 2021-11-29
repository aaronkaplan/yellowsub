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

