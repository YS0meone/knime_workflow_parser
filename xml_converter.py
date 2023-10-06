import json
import xmltodict
from operator_generator import OperatorGenerator


XML_FILE_PATH = "converter\simple.xml"
JSON_FILE_PATH = "converter\output.json"
CURRENT_OUTPUT = "converter\progress.json"

workflow_temp = {
            "operators": [],
            "operatorPositions": {},
            "links": [],
            "groups": [],
            "breakpoints": {},
            "commentBoxes": []
        }

mapping_table = {
                "read_csv": "CSVFileScan",
                "blending:select_attributes": "Projection",
                "aggregate": "Aggregate"
                }

def read_xml(path):
    with open(path, 'r') as xml_file:
        data_dict = xmltodict.parse(xml_file.read(), dict_constructor=dict)
    return data_dict["process"]["operator"]["process"]

def get_output(path, data):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    

def main():
    # parse xml
    rm_dict = read_xml(XML_FILE_PATH)
    tx_dict = workflow_temp.copy()
    get_output(JSON_FILE_PATH, rm_dict)

    # generate show result operator

    # create the operator dict
    for operator in rm_dict["operator"]:
        op_type = mapping_table[operator["@class"]]
        og = OperatorGenerator(op_type, operator)
        tx_dict["operators"].append(og.get_temp())
        tx_dict["operatorPositions"][og.get_id()] = og.generate_pos()
    # get operator position
    get_output(CURRENT_OUTPUT, tx_dict)
    # get connects



    # generate tx_dict
    # for operator in rm_dict["operator"]:
    #     print(operator)
        # if operator["@class"] in mapping_table:

    


if __name__ == "__main__":
    main()