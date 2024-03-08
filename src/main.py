import json
import xmltodict
from pprint import pprint
from typing import Dict
from operator_generator import OperatorGenerator
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
    template["source"]["operatorID"] = mapping[sourceID]
    template["source"]["portID"] = "output-" + str(sourcePort - 1)
    template["target"]["operatorID"] = mapping[destID]
    template["target"]["portID"] = "input-" + str(destPort - 1)

    return template

def main():
    # get the root path from the system arguments
    args = parse_args()
    root_path = args.input
    knime_path = root_path / "workflow.knime"
    output_path = args.output
    config_path = args.config
    try:
        # check if we need to convert workflow.knime
        xml_path = root_path / "workflow.xml"
        if knime_path.exists():
            shutil.copy(knime_path, xml_path)
        elif not xml_path.exists():
            raise FileNotFoundError("Neither workflow.xml nor workflow.knime exist")
    except FileNotFoundError as e:
        print(f"Error occurred when looking for metadata: {e}")
    except IOError as e:
        print(f"Error occurred while creating workflow.xml: {e}")
    # preprocess the input workflow
    xml_dict = parse_xml(xml_path)
    kn_dict = {}
    format_dict(xml_dict, kn_dict)
    # the dictionary representation of the knime workflow in dict
    kn_dict = kn_dict["workflow.knime"]
    tx_dict = TEXERA_WORKFLOW_TEMPLATE
    # the operatorID mapping between knime and texera
    k2t_id_mapping = {}
    kn_ops_setting = kn_dict["nodes"]

    # parsing the operator part
    # The mapping direction: Knime -> Texera
    tx_dict["commentBoxes"] = []
    for kn_op_setting in kn_ops_setting.values():
        # get the operator type of the knime operator
        kn_op_type = get_knime_operator_type(kn_op_setting["node_settings_file"])
        # initialize an operator generator to create operator elements in texera workflow
        og = OperatorGenerator(kn_op_type, kn_op_setting, root_path, config_path)
        tx_dict["operators"].append(og.get_temp())
        tx_dict["operatorPositions"][og.get_id()] = og.generate_pos()
        
        temp_website = "https://hub.knime.com/knime/extensions/org.knime.features.base/latest/org.knime.base.node.io.filehandling.csv.reader.CSVTableReaderNodeFactory"
        temp_time = "2024-03-08T10:36:49.883Z"
        tx_dict["commentBoxes"].append(og.generate_comment_box(
            temp_website,
            "Bot",
            1,
            temp_time
        ))
        k2t_id_mapping[kn_op_setting["id"]] = og.get_id()

    # parsing the connection part
    connections = kn_dict["connections"]
    for connection in connections.values():
        tx_dict["links"].append(generate_link(k2t_id_mapping, connection))
    generate_texera_workflow(output_path, tx_dict)


if __name__ == "__main__":
    main()

