from lib.processor.enricher import Enricher

import socket


# see https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
# thanks stackoverflow

def get_ips_by_dns_lookup(target, port=None):
    '''
        this function takes the passed target and optional port and does a dns
        lookup. it returns the ips that it finds to the caller.

        :param target:  the URI that you'd like to get the ip address(es) for
        :type target:   string
        :param port:    which port do you want to do the lookup against?
        :type port:     integer
        :returns ips:   all of the discovered ips for the target
        :rtype ips:     list of strings

    '''
    import socket

    if not port:
        port = 443

    return list(map(lambda x: x[4][0], socket.getaddrinfo('{}.'.format(target),port,type=socket.SOCK_STREAM)))


class GetHostByName(Enricher):
    """A very simple / KISS gethostbyname enricher. It will fetch the "fqdn" key-value pair from the message and add a list of IPs to the message """
    dns_recursor = "8.8.8.8"

    def process(self, channel = None, method = None, properties = None, msg: dict = {}):
        fqdn = msg.get('fqdn', None)
        if fqdn:
            ips = get_ips_by_dns_lookup(fqdn)
        msg['ips'] = ips
        return ips


if __name__ == "__main__":
    ips = get_ips_by_dns_lookup(target='example.com')
    print(ips)
    assert '93.184.216.34' in ips

    e = GetHostByName()
    newmsg = e.process("ch1", msg = { "fqdn": "example.com" } )
    assert 'ips' in newmsg.keys() and '93.184.216.34' in newmsg['ips']
