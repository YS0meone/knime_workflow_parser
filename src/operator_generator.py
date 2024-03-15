import uuid
import yaml
import xmltodict
from pathlib import Path
from node_retriever import NodeRetriever
from utils import format_dict
from typing import Dict

class OperatorGenerator():
    """
        OperatorGenerator takes in knime operator type and the dict representation of the operator to create an operator section in the texera workflow. Itrequres a .json file which specify the mapping between the knime operator type and the texera operator template
    """

    def __init__(self, knime_operator_type: str, node_setting: dict, root_path: Path, config_path: Path, input_ports_setting: Dict[str, int]) -> None:
        # loads the .json as dictionary
        self._temp = {
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
        mapping_yaml = open(config_path, "r")
        self.mapping_config = yaml.safe_load(mapping_yaml)
        mapping_yaml.close()
        self.knime_operator_type = knime_operator_type
        self.node_setting = node_setting
        self.input_ports_setting = input_ports_setting
        self.x = float(self.node_setting["ui_settings"]["extrainfo.node.bounds"]["0"])
        self.y = float(self.node_setting["ui_settings"]["extrainfo.node.bounds"]["1"])
        # read the settings xml file and save it as dict
        path = root_path / self.node_setting["node_settings_file"]
        with open(path, 'r') as xml_file:
            self.source_xml = xml_file.read()
            xml_dict = xmltodict.parse(
                self.source_xml, dict_constructor=dict)
        self.settings = {}
        format_dict(xml_dict, self.settings)
        self.settings = self.settings["settings.xml"]
        # set up the basic template for this particular knime operator type
        self.convert()

    def convert(self) -> None:
        # generate the basic template if we cannot find the mapping we use the template of dummy op
        if self.knime_operator_type in self.mapping_config:
            self._temp.update(self.mapping_config[self.knime_operator_type]["operator_specs"])
            self._temp["customDisplayName"] = self._temp["operatorType"]

        else:
            self._temp.update(self.mapping_config["Dummy"]["operator_specs"])
            # dynamically generate input and output ports
            input_ports_count = self.input_ports_setting[self.node_setting["id"]]
            output_ports_count = len(list(self.settings["ports"].values()))
            self._temp["inputPorts"] = []
            self._temp["outputPorts"] = []
            for i in range(input_ports_count):
                input_port = {
                    "portID": f"input-{i}",
                    "displayName": "",
                    "allowMultiInputs": True,
                    "isDynamicPort": True
                }
                self._temp["inputPorts"].append(input_port)
            for i in range(output_ports_count):
                output_port = {
                    "portID": f"output-{i}",
                    "displayName": "",
                    "isDynamicPort": True
                }
                self._temp["outputPorts"].append(output_port)
            self._temp["customDisplayName"] = self.knime_operator_type
        # generate the operatorID for the operator
        self._temp["operatorID"] = self.generate_id(self._temp["operatorType"])

        # check if we want to map the property or if the operator is covered in the config file
        if self.knime_operator_type in self.mapping_config:
            prop_map = self.mapping_config[self.knime_operator_type]["property_mapping"]
            properties = self._temp["operatorProperties"]
            NR = NodeRetriever(self.settings)
            # loop thru each property and config pair
            for prop, config in prop_map.items():
                # first check if the property is dynamic or not
                print("Now retrieving", prop)
                try:
                    properties[prop] = NR.retrieve_nodes(
                        config["nodes"], config["action"])
                except ValueError as e:
                    print(f"Error occured while retrieving node: {e}")
        # we want to store the whole xml file into the dummy prop
        else:
            self._temp["operatorProperties"]["dummyPropertyList"] = []
            dum_prop_list = self._temp["operatorProperties"]["dummyPropertyList"]
            dum_prop = {}
            dum_prop["dummyProperty"] = "Source XML"
            dum_prop["dummyValue"] = self.source_xml
            dum_prop_list.append(dum_prop)

    def get_temp(self) -> dict:
        return self._temp

    def generate_id(self, texera_operator_type) -> str:
        return texera_operator_type + "-" + "operator" + "-" + str(uuid.uuid4())

    def get_id(self) -> str:
        return self._temp["operatorID"]

    def generate_pos(self) -> dict:
        return {"x": self.x, "y": self.y}
    
    def generate_comment_box(self, content: str, creator_name: str, creator_id: int, creation_time: str):
        comment_box = {}
        comment_box["commentBoxID"] = self.generate_boxid()
        comment_box["comments"] = []
        comment_box["comments"].append(self.generate_comment(content, creator_name, creator_id, creation_time))
        comment_box["commentBoxPosition"] = self.generate_comment_pos()
        return comment_box
    
    def generate_boxid(self):
        return "commentBox-" + str(uuid.uuid4())
    
    def generate_comment(self, content: str, creator_name: str, creator_id: int, creation_time: str):
        comment = {}
        comment["content"] = content
        comment["creatorName"] = creator_name
        comment["createorID"] = creator_id
        comment["creationTime"] = creation_time
        return comment

    def generate_comment_pos(self):
        return {"x": self.x + 60, "y": self.y + 30}
