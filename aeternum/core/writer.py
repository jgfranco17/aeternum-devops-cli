from collections import OrderedDict

import yaml


class OrderedDumper(yaml.Dumper):
    def represent_mapping(self, tag, mapping, **kwargs):
        mapping = OrderedDict(mapping)
        return super().represent_mapping(tag, mapping, **kwargs)
