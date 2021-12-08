import logging
import socket
import uuid
from lib.processor.enricher import Enricher


# see https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
# thanks stackoverflow


def get_ips_by_dns_lookup(fqdn, port=None):
    """
        this function takes the passed fqdn and optional port and does a dns
        lookup. it returns the ips that it finds to the caller.

        :param fqdn:    the URI that you'd like to get the ip address(es) for
        :type fqdn:     string
        :param port:    which port do you want to do the lookup against?
        :type port:     integer
        :returns ips:   all of the discovered ips for the fqdn
        :rtype ips:     list of strings
    """

    try:
        l = list(map(lambda x: x[4][0], socket.getaddrinfo(fqdn, port, proto = socket.IPPROTO_TCP)))
    except Exception as ex:
        logging.info("Could not resolve domain %s. Reason: %s" % (fqdn, str(ex)))
        return []
    return l


class GetHostByName(Enricher):
    """A very simple / KISS gethostbyname enricher. It will fetch the "fqdn" key-value pair from the message and add a list of IPs to the message """
    dns_recursor = "8.8.8.8"

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        fqdn = msg.get('fqdn', None)
        self.logger.warn("(warning) about to log %s" %fqdn)
        self.logger.info("here is some info for %s" %fqdn)
        if fqdn:
            ips = get_ips_by_dns_lookup(fqdn)
            msg['ips'] = ips
        return msg


PROCESSOR=GetHostByName

if __name__ == "__main__":
    ips = get_ips_by_dns_lookup(fqdn = 'example.com')
    print(ips)
    assert '93.184.216.34' in ips

    e = GetHostByName(processor_id = "sample-gethostbyname")
    newmsg = e.process("ch1", msg = {"fqdn": "example.com"})
    print(newmsg)
    assert 'ips' in newmsg.keys() and '93.184.216.34' in newmsg['ips']

    # negative test case: there is no ip for this domain
    newmsg = e.process("ch1", msg = {"fqdn": "{}.com".format(uuid.uuid4())})
    assert 'ips' in newmsg.keys() and len(newmsg['ips']) == 0

    # IPv6 test case
    newmsg = e.process("ch1", msg = {"fqdn": "ipv6.google.com"})
    print(newmsg)
    assert 'ips' in newmsg.keys() and '2a00:1450:4016:' in newmsg['ips'][0]

