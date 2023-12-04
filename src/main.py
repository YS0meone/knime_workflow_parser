import json
import xmltodict
from pprint import pprint
from operator_generator import OperatorGenerator
import re
import uuid
from pathlib import Path
import os
import argparse

# texera workflow template
workflow_temp = {
    "operators": [],
    "operatorPositions": {},
    "links": [],
    "groups": [],
    "breakpoints": {},
    "commentBoxes": []
}


def parse_args():
    """
        Parse the system arguments and return them
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True,
                        help="Path to the directory of the workflow")
    parser.add_argument("--output", type=Path, required=True,
                        help="Path to the output folder")
    parser.add_argument("--config", type=Path, required=True,
                        help="Path to the mapping config file")
    args = parser.parse_args()
    return args


def read_xml(path):
    """
        read the knime workflow xml file and convert to the dictionary
    """
    with open(path, 'r', encoding="utf-8") as xml_file:
        data_dict = xmltodict.parse(
            xml_file.read(), dict_constructor=dict)
        return data_dict


def get_output(path, data):
    """
        dump the dictionary as json file for texera to read
    """
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def remove_pattern(input_str):
    """
        remove the pattern to get the knime's operator type
    """
    pattern = r' \(\#\d+\)/settings.xml'
    return re.sub(pattern, '', input_str)


def generate_link(mapping, connection):
    """
        Given the operatorID mappings between knime and texera, and the connection section of knime, create connection element in the texera workflow to generate links
    """
    template = {
        "linkID": "link-"+str(uuid.uuid4()),
        "source": {
            "operatorID": "",
            "portID": ""
        },
        "target": {
            "operatorID": "",
            "portID": ""
        }
    }
    sourceID = connection["sourceID"]
    sourcePort = int(connection["sourcePort"])
    destID = connection["destID"]
    destPort = int(connection["destPort"])
    template["source"]["operatorID"] = mapping[sourceID]
    template["source"]["portID"] = "output-" + str(sourcePort - 1)
    template["target"]["operatorID"] = mapping[destID]
    template["target"]["portID"] = "input-" + str(destPort - 1)

    return template


def format_dict(xml_dict, ret_dict):
    """
        Further process the parse Knime workflow dictionary to make the keys and values more meaningful
    """
    if "entry" in xml_dict:
        if isinstance(xml_dict["entry"], list):
            for entry in xml_dict["entry"]:
                ret_dict[entry["@key"]] = entry["@value"]
        else:
            ret_dict[xml_dict["entry"]["@key"]] = xml_dict["entry"]["@value"]
    if "config" in xml_dict:
        if isinstance(xml_dict["config"], list):
            for config in xml_dict["config"]:
                ret_dict[config["@key"]] = {}
                format_dict(config, ret_dict[config["@key"]])
        else:
            ret_dict[xml_dict["config"]["@key"]] = {}
            format_dict(xml_dict["config"],
                        ret_dict[xml_dict["config"]["@key"]])
    return


def main():
    # get the root path from the system arguments
    args = parse_args()
    root_path = args.input
    xml_path = root_path / "workflow.xml"
    output_path = args.output
    config_path = args.config
    try:
        # check if we need to convert workflow.knime
        if not xml_path.exists():
            knime_path = root_path / "workflow.knime"
            if knime_path.exists():
                knime_path.rename(xml_path)
            else:
                raise FileNotFoundError(
                    "Knime workflow.knime not found, invalid workflow!")
    except FileNotFoundError as e:
        print(e)

    # preprocess the input workflow
    xml_dict = read_xml(xml_path)
    kn_dict = {}
    format_dict(xml_dict, kn_dict)
    # the dictionary representation of the knime workflow in dict
    kn_dict = kn_dict["workflow.knime"]

    tx_dict = workflow_temp.copy()
    # the operatorID mapping between knime and texera
    k2t_mapping = {}
    kn_ops = kn_dict["nodes"]

    # parsing the operator part
    # The mapping direction: Knime -> Texera
    for op in kn_ops.values():
        # get the operator type of the knime operator
        op_type = remove_pattern(op["node_settings_file"])
        # initialize an operator generator to create operator elements in texera workflow
        og = OperatorGenerator(op_type, op, root_path, config_path)
        tx_dict["operators"].append(og.get_temp())
        tx_dict["operatorPositions"][og.get_id()] = og.generate_pos()
        k2t_mapping[op["id"]] = og.get_id()

    # parsing the connection part
    connections = kn_dict["connections"]
    for connection in connections.values():
        tx_dict["links"].append(generate_link(k2t_mapping, connection))
    get_output(output_path, tx_dict)


if __name__ == "__main__":
    main()
