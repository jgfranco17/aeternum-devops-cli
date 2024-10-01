from collections import OrderedDict

import yaml


class OrderedDumper(yaml.Dumper):
    def represent_mapping(self, tag, mapping, **kwargs):
        mapping = OrderedDict(mapping)
        return super().represent_mapping(tag, mapping, **kwargs)

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
