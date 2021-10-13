import sys
from censys.search import CensysHosts


h = CensysHosts()

# Fetch a list of host names for the specified IP address.
names = h.view_host_names(sys.argv[1])
print(names)
