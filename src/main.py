import json
import xmltodict
from typing import Dict
from operator_generator import OperatorGenerator
from collections import defaultdict
import re
import uuid
from pathlib import Path
import argparse
import shutil
from utils import format_dict

# texera workflow template
TEXERA_WORKFLOW_TEMPLATE = {
    "operators": [],
    "operatorPositions": {},
    "links": [],
    "groups": [],
    "breakpoints": {},
    "commentBoxes": []
}


def parse_args() -> argparse.Namespace:
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


def parse_xml(path: str | Path) -> dict:
    """
        read the knime workflow xml file and convert to the dictionary
    """
    with open(path, 'r', encoding="utf-8") as xml_file:
        data_dict = xmltodict.parse(
            xml_file.read(), dict_constructor=dict)
        return data_dict


def generate_texera_workflow(path: str | Path, data: dict) -> None:
    """
        dump the dictionary as json file for texera to read
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def get_knime_operator_type(filename: str) -> str:
    """
        remove the pattern in the filename to get the knime's operator type
    """
    pattern = r' \(\#\d+\)/settings.xml'
    return re.sub(pattern, '', filename)


def get_input_ports_settting(kn_connection_section: Dict[str, str]) -> Dict[str, int]:
    """
        Get the knime connection setting and retrieve the input ports number of each operator
    """
    input_ports_setting = defaultdict(int)
    for connection_setting in kn_connection_section.values():
        destID = connection_setting["destID"]
        destPort = int(connection_setting["destPort"])
        input_ports_setting[destID] = max(input_ports_setting[destID], destPort)
    return input_ports_setting

def generate_link(mapping: Dict[str, str], connection: dict) -> dict:
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
    # a metanode would have one to many mapping
    if isinstance(mapping[sourceID], dict):
        # need to iterative retrieve the preimage
        preimage = mapping[sourceID]["output"][sourcePort]
        # iteratively check if we found the real preimage
        while isinstance(preimage[0], dict):
            sourcePort = int(preimage[1])
            preimage = preimage[0]["output"][sourcePort]
        template["source"]["operatorID"] = preimage[0]
        template["source"]["portID"] = "output-" + str(int(preimage[1]) - 1)
    else:
        template["source"]["operatorID"] = mapping[sourceID]
        template["source"]["portID"] = "output-" + str(sourcePort - 1)
    if isinstance(mapping[destID], dict):
        preimage = mapping[destID]["input"][destPort]
        while isinstance(preimage[0], dict):
            sourcePort = int(preimage[1])
            preimage = preimage[0]["input"][destPort]
        template["target"]["operatorID"] = preimage[0]
        template["target"]["portID"] = "input-" + str(int(preimage[1]) - 1)
    else:
        template["target"]["operatorID"] = mapping[destID]
        template["target"]["portID"] = "input-" + str(destPort - 1)
    return template


def get_knime_workflow(root_path: Path, knime_workflow: dict):
    """
        This function takes in the directory of the Knime workflow, locates and converts the workflow.knime into xml
        file. Then it dumps the xml file as a Python dictionary and formats it.
    """
    knime_path = root_path / "workflow.knime"
    xml_path = root_path / "workflow.xml"
    try:
        # check if we need to convert workflow.knime
        if knime_path.exists():
            shutil.copy(knime_path, xml_path)
        elif not xml_path.exists():
            raise FileNotFoundError("Neither workflow.xml nor workflow.knime exist")
    except FileNotFoundError as e:
        print(f"Error occurred when looking for metadata: {e}")
    except IOError as e:
        print(f"Error occurred while creating workflow.xml: {e}")
    # preprocess the input workflow
    xml_workflow = parse_xml(xml_path)
    format_dict(xml_workflow, knime_workflow)


def parsing_workflow(root_path: Path, config_path: Path, texera_workflow: dict, k2t_id_mapping: dict) -> dict:
    """
        This is the recursive workflow parsing function. It would parse and convert each Knime node into
        Texera operator. If a metanode exists then it would recursively parse the internal worklfow. The function
        would return a dictionary specifying the mapping from metanode's port to Texera operator's UUID and port
    """
    # retrieve knime's workflow
    knime_workflow = {}
    get_knime_workflow(root_path, knime_workflow)
    # the dictionary representation of the knime workflow in dict
    knime_workflow = knime_workflow["workflow.knime"]
    knime_operator_settings = knime_workflow["nodes"]
    # parsing the operator part
    # Get the number of input ports
    input_port_setting = get_input_ports_settting(knime_workflow["connections"])
    for kn_op_setting in knime_operator_settings.values():
        # check if the node type is metanode
        if kn_op_setting["node_is_meta"] == "true":
            # if it is the metanode we recursively calles the parsing workflow with a new root_path
            new_root_path = (root_path / kn_op_setting["node_settings_file"]).parent
            # port2ID
            port2ID = parsing_workflow(
                new_root_path,
                config_path,
                texera_workflow,
                k2t_id_mapping
                )
            k2t_id_mapping[kn_op_setting["id"]] = port2ID
            # portID is 0 based only for metanode correct it here
            connections = knime_workflow["connections"]
            for connection in connections.values():
                if connection["sourceID"] == kn_op_setting["id"]:
                    old_port_id = int(connection["sourcePort"])
                    connection["sourcePort"] = str(old_port_id + 1)
                if connection["destID"] == kn_op_setting["id"]:
                    old_port_id = int(connection["destPort"])
                    connection["destPort"] = str(old_port_id + 1)
            continue
        # get the operator type of the knime operator
        kn_op_type = get_knime_operator_type(kn_op_setting["node_settings_file"])
        # initialize an operator generator to create operator elements in texera workflow
        og = OperatorGenerator(kn_op_type, kn_op_setting, root_path, config_path, input_port_setting)
        texera_workflow["operators"].append(og.get_temp())
        texera_workflow["operatorPositions"][og.get_id()] = og.generate_pos()
        temp_website = "https://hub.knime.com/knime/extensions/org.knime.features.base/latest/org.knime.base.node.io.filehandling.csv.reader.CSVTableReaderNodeFactory"
        temp_time = "2024-03-08T10:36:49.883Z"
        texera_workflow["commentBoxes"].append(og.generate_comment_box(
            temp_website,
            "Bot",
            1,
            temp_time
        ))
        k2t_id_mapping[kn_op_setting["id"]] = og.get_id()
    # parsing the connection part
    operator_id = -1
    # The mapping between metanode port and Texera Operator UUID & port
    port2ID = {"input": {}, "output": {}}
    connections = knime_workflow["connections"]
    for connection in connections.values():
        # check if it the destID is representing the output port of metanode
        if connection["sourceID"] == "-1":
            operator_id = k2t_id_mapping[connection["destID"]]
            port = int(connection["sourcePort"]) + 1
            port2ID["input"][port] = operator_id, connection["destPort"]
            continue
        if connection["destID"] == "-1":
            operator_id = k2t_id_mapping[connection["sourceID"]]
            port = int(connection["destPort"]) + 1
            port2ID["output"][port] = operator_id, connection["sourcePort"]
            continue
        texera_workflow["links"].append(generate_link(k2t_id_mapping, connection))
    return port2ID


def main():
    # get the root path from the system arguments
    args = parse_args()
    root_path = args.input
    output_path = args.output
    config_path = args.config
    texera_workflow = TEXERA_WORKFLOW_TEMPLATE
    # the operatorID mapping between knime and texera
    k2t_id_mapping = {}
    # parse the workflow recursively to deal with metanode
    parsing_workflow(
        root_path,
        config_path,
        texera_workflow,
        k2t_id_mapping
        )
    generate_texera_workflow(output_path, texera_workflow)


if __name__ == "__main__":
    main()
