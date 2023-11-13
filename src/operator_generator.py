import uuid
import json
from pprint import pprint
from collections import deque
import xmltodict
import os
from pathlib import Path


class OperatorGenerator():
    """
        OperatorGenerator takes in knime operator type and the dict representation of the operator to create an operator section in the texera workflow. Itrequres a .json file which specify the mapping between the knime operator type and the texera operator template
    """

    def __init__(self, operator_type, input_dict, root_path, config_path):
        # loads the .json as dictionary
        mapping_json = open(config_path, "r")
        self.mapping_config = json.load(mapping_json)
        mapping_json.close()
        self.type = operator_type
        self.input = input_dict
        # read the settings xml file and save it as dict
        path = root_path / self.input["node_settings_file"]
        with open(path, 'r') as xml_file:
            xml_dict = xmltodict.parse(
                xml_file.read(), dict_constructor=dict)
        self.settings = {}
        self.format_dict(xml_dict, self.settings)
        self.settings = self.settings["settings.xml"]
        # set up the basic template for this particular knime operator type
        self.convert()

    def convert(self):
        # generate the basic template if we cannot find the mapping we use the template of dummy op
        if self.type in self.mapping_config:
            self.temp = self.mapping_config[self.type]["operator_template"]
        else:
            self.temp = self.mapping_config["Dummy"]["operator_template"]
            self.temp["customDisplayName"] = self.type
        # generate the operatorID for the operator
        self.temp["operatorID"] = self.generate_id(self.temp["operatorType"])

        # check if we want to map the attribute or if the operator is covered in the config file
        if self.type in self.mapping_config and self.mapping_config[self.type]["map_attribute"]:
            attr_map = self.mapping_config[self.type]["attribute_mapping"]
            properties = self.temp["operatorProperties"]
            # loop thru each property and config pair
            for prop, config in attr_map.items():
                # print(prop, config)
                # first check if the property is dynamic or not
                if config["attr_type"] == "dynamic":
                    prop_group = {}
                    for p, c in config["group"].items():
                        prop_group[p] = self.get_property_val(c)
                    properties[prop].append(prop_group)
                elif config["attr_type"] == "multi":
                    properties[prop].append(self.get_property_val(config))
                elif config["attr_type"] == "default":
                    properties[prop] = self.get_property_val(config)
                    # print(prop, properties[prop])

    def get_property_val(self, config):
        if config["method"] == "type_casting":
            value = self.find_node(config["route"])
            # in case we didn't find the node
            if value == None:
                return None
            type_cast = __builtins__[config["type"]]
            return type_cast(value)
        elif config["method"] == "conditional_type_casting":
            if self.find_node(config["condition"]["flag"]) == config["condition"]["value"]:
                value = self.find_node(config["route"])
                if value == None:
                    return None
                type_cast = __builtins__[config["type"]]
                return type_cast(value)
        elif config["method"] == "value_mapping":
            value = self.find_node(config["route"])
            if value == None:
                return None
            if value in config["map"]:
                return config["map"][value]

    def find_node(self, stops):
        """
            Returns the node value in the self.settings
        """
        # we check before we put the element inside the deque
        # the element inside deque is guaranteed to be dictionary

        def helper(start, stop):
            q = deque([start])
            while q:
                cur = q.popleft()
                for key in cur.keys():
                    if key == stop:
                        return cur[key]
                    else:
                        if isinstance(cur[key], dict):
                            q.append(cur[key])
            return None
        start = self.settings
        for stop in stops:
            if not isinstance(start, dict):
                return None
            start = helper(start, stop)
        return start

    def format_dict(self, xml_dict, ret_dict):
        """
            Further process the parse Knime workflow dictionary to make the keys and values more meaningful
        """
        if "entry" in xml_dict:
            if isinstance(xml_dict["entry"], list):
                for entry in xml_dict["entry"]:
                    ret_dict[entry["@key"]] = entry["@value"]
            else:
                ret_dict[xml_dict["entry"]["@key"]
                         ] = xml_dict["entry"]["@value"]
        if "config" in xml_dict:
            if isinstance(xml_dict["config"], list):
                for config in xml_dict["config"]:
                    ret_dict[config["@key"]] = {}
                    self.format_dict(config, ret_dict[config["@key"]])
            else:
                ret_dict[xml_dict["config"]["@key"]] = {}
                self.format_dict(xml_dict["config"],
                                 ret_dict[xml_dict["config"]["@key"]])
        return

    def get_temp(self):
        return self.temp

    def generate_id(self, operator_type):
        return operator_type + "-" + "operator" + "-" + str(uuid.uuid4())

    def get_id(self):
        return self.temp["operatorID"]

    def generate_pos(self):
        """get the position of the knime's operator. NOTICE: MIGHT BE BOUNDARY ISSUE. SHOULD TEST FOR BOUNDARY IF NEEDED"""
        return {"x": float(self.input["ui_settings"]["extrainfo.node.bounds"]["0"]), "y": float(self.input["ui_settings"]["extrainfo.node.bounds"]["1"])}
