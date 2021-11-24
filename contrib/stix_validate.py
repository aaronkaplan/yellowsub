# stolen from https://stix2-validator.readthedocs.io/en/latest/usage.html
import sys
from stix2validator import validate_file, print_results

results = validate_file(sys.argv[1])
print_results(results)
