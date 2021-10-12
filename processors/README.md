# Processors

Here you can add all processors in their respective folders:

* collectors ... for processors which can *collect* data from external sources (filesystem, splunk, etc.)
* parsers ...... for processors which shall *map* the external data collected from the collectors to the internal dataformat standard
* enrichers..... for enrichers. They operate on the internal data format
* filters ...... for filters which let a message through or not (based on some filter rules)
* output........ for output processors which shall send the data to some output destination (such as Jira, splunk, etc.)
