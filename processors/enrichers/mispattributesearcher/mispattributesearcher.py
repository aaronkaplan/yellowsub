from lib.processor.enricher import Enricher
from pymisp import PyMISP


class MispAttributeSearcher(Enricher):
    """TODO: here goes a class description"""
    # How is configuration passed in at object creation?
    # How will this object be called from the other code?

    # TODO:  implement logging globally
    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)
        c=self.config
        try:
            self.misp_url = c["processors"][self.__class__.__name__]["misp_uri"]
            self.misp_api_key = c["processors"][self.__class__.__name__]["misp_api_key"]
        except KeyError as e:
            raise RuntimeError("could not load config for MispAttributeSearcher Reason: {}".format(str(e)))
        try:
            self.misp_connection = PyMISP(self.misp_url, self.misp_api_key, False, 'json')
        except Exception as e:
            raise RuntimeError("could not open MISP connection in MispAttributeSearcher Reason: {}".format(str(e)))

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        # TODO:  This has to contain the value we are searching for in attributes
        # TODO:  Implement partial string search
        # TODO:  documentation for methods
        value = msg["search_value"]
        ret = self.misp_connection.search(controller="attributes", return_format="json", value=value)
        if len(ret["Attribute"]) == 0:
            return (False, msg)
        else:
            # TODO:  message appending and validation should not happen in an enricher
            msg["misp_attributes"] = {}
            # TODO:  create frendly names for misp instances based on url in class constructor
            # TODO:  tidy up the dict for misp instance and attribute retrieval
            #       (array of dicts or whatever makes more sense)
            msg["misp_attributes"] = []
            instance_retrieved_data = {}
            instance_retrieved_data["misp_instance"] = self.misp_url
            instance_retrieved_data["matched_attributes"] = []
            for att in ret["Attribute"]:
                instance_retrieved_data["matched_attributes"].append(att)
            msg["misp_attributes"].append(instance_retrieved_data)
            return (True, msg)


if __name__ == "__main__":
    '''debugging'''
    msg={}
    msg["search_value"] = "88.132.150.82"
    ms = MispAttributeSearcher("313")
    c = ms.config
    print(c)
    found, message = ms.process(channel=None, method=None, properties=None, msg=msg)
    print("MAMA")

    '''end of debugging'''

    # TODO   Question?: How will this scale? How do you instantiate different enrichers with different config unless
    #            the config is selfcontained or passed at instantiation time?
    #            If we go down the route of having multiple enrichers of the same type
    #            with their config in the same folder. How do you know which config to read at instantiation time?
    # TODO:  parse config and validate config
    # TODO:  message.get
    # TODO:  verify input data
    # TODO:  query misp instance based on input data
    # TODO:  populate message with result
    # TODO:  Validate message as per the schema
    # TODO:  Return message
