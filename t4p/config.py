import os
import sys
import yaml

base_path = os.path.realpath(sys.argv[0]) if sys.argv[0] else None
base_path = "/".join(base_path.split("/")[:-1])

config_file = os.path.join(base_path, 'config.yml')

with open(config_file) as cfg_file:
	config = yaml.load(cfg_file)

