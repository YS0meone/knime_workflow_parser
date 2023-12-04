import uuid
import json
from pprint import pprint
from collections import deque
import xmltodict
import os
from pathlib import Path
from NodeRetriever import NodeRetriever
from copy import deepcopy

_BACKBONE = {
    "operatorID": "",
    "operatorType": "",
    "operatorVersion": "",
    "operatorProperties": {},
    "inputPorts": [],
    "outputPorts": [],
    "showAdvanced": False,
    "isDisabled": False,
    "customDisplayName": "",
    "dynamicInputPorts": False,
    "dynamicOutputPorts": False
}


class OperatorGenerator():
    """
        OperatorGenerator takes in knime operator type and the dict representation of the operator to create an operator section in the texera workflow. Itrequres a .json file which specify the mapping between the knime operator type and the texera operator template
    """

    def __init__(self, operator_type: str, input_dict: dict, root_path: Path, config_path: Path) -> None:
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

    def convert(self) -> None:
        # generate the basic template if we cannot find the mapping we use the template of dummy op
        self._temp = deepcopy(_BACKBONE)
        # pprint(self._temp)
        if self.type in self.mapping_config:
            self._temp.update(self.mapping_config[self.type]["operator_specs"])
            self._temp["customDisplayName"] = self._temp["operatorType"]
            # pprint(self._temp)
        else:
            self._temp.update(self.mapping_config["Dummy"]["operator_specs"])
            self._temp["customDisplayName"] = self.type
        # generate the operatorID for the operator
        self._temp["operatorID"] = self.generate_id(self._temp["operatorType"])

        # check if we want to map the property or if the operator is covered in the config file
        if self.type in self.mapping_config:
            prop_map = self.mapping_config[self.type]["property_mapping"]
            properties = self._temp["operatorProperties"]
            NR = NodeRetriever(self.settings)
            # loop thru each property and config pair
            for prop, config in prop_map.items():
                # print(prop, config)
                # first check if the property is dynamic or not
                properties[prop] = NR.retrieve_node(
                    config["paths"], config["action"])

    def get_temp(self):
        return self._temp

    def generate_id(self, operator_type):
        return operator_type + "-" + "operator" + "-" + str(uuid.uuid4())

    def get_id(self):
        return self._temp["operatorID"]

    def generate_pos(self):
        """get the position of the knime's operator. NOTICE: MIGHT BE BOUNDARY ISSUE. SHOULD TEST FOR BOUNDARY IF NEEDED"""
        return {"x": float(self.input["ui_settings"]["extrainfo.node.bounds"]["0"]), "y": float(self.input["ui_settings"]["extrainfo.node.bounds"]["1"])}
