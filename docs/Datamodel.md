# Dataformat

a.k.a. "datamodel". We will use the words "datamodel" and "dataformat" interchangeably.


# Basic ideas

We are going to use a very thin, JSON based header (wrapper) around the data (`payload`).

* The dataformat shall be defined in a JSON Schema (the *"message schema"*). It resides in `lib/datamodel/yellowsub_schema.json`.
* The message schema defines all possible messages.
* Each message MUST validate against the message JSON schema.
* The code for checking and parsing the yellowsub dataformat resides in `lib/datamodel.py`.
* The `payload` of a message MUST validate against any of the `lib/datamodel/**.json` sub-schemas. 
  Example: if `format: "domain-name"`, then the `type` field shall be `STIX-2.1` and the `payload` field shall validate
  against `lib/datamode/observables/domain-name.json`


# Header field definitions and meaninings

| Field     | Meaning   |
| --------- | ----------|
| `format`  | 

# Example datamodel message - flat event

```json
{
  "format": "cth-event-data-format",
  "version": 1,
  "type": "event",
  "meta": {
    "uuid": "25c9487c-1ae9-11ec-99a3-b3a261e8732d",
    "relations": [
      {
        "type": "is_parent_of",
        "right_side": "38bd847a-1ae9-11ec-a308-ef1417ea8564"
      }
    ]
  },
  "payload": {
    "source.ip": "127.0.0.1",
    "source.fqdn": "example.com",
    "riskiq.domains": [ "a.b.com", "c.d.com" ]
  }
}
```

This example has a message of format "cth-event-data-format" (a custom format defined for sharing flat dicts to a ticket system).

# Example STIX-2.1 datamodel - observable

```json
{
  "format": "domain-name",
  "version": 1,
  "type": "STIX-2.1",
  "meta": {
    "uuid": "25c9487c-1ae9-11ec-99a3-b3a261e8732d",
    "relations": [
      {
        "type": "is_parent_of",
        "right_side": "38bd847a-1ae9-11ec-a308-ef1417ea8564"
      }
    ]
  },
  "payload": {
    ... < stix-2.1 domain name observable goes here> ...
  }
}
```