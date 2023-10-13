import json
import xmltodict
from pprint import pprint
from knime_operator_generator import OperatorGenerator
import re

XML_FILE_PATH = "workflow.xml"
JSON_FILE_PATH = "output.json"
CURRENT_OUTPUT = "progress.json"

workflow_temp = {
            "operators": [],
            "operatorPositions": {},
            "links": [],
            "groups": [],
            "breakpoints": {},
            "commentBoxes": []
        }



def read_xml(path):
    with open(path, 'r') as xml_file:
        data_dict = xmltodict.parse(xml_file.read(), dict_constructor=dict)
        return(data_dict['config']['config'])
    

def get_output(path, data):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
def remove_pattern(input_str):
    pattern  = r' \(\#\d+\)/settings.xml'
    return re.sub(pattern, '', input_str)

def main():
    # parse xml
    kn_dict = read_xml(XML_FILE_PATH)
    # pprint(kn_dict)
    kn_ops = kn_dict[2]["config"]
    # pprint(kn_ops)
    for op in kn_ops:
        op_type = op['entry'][1]['@value']
        print(remove_pattern(op_type))
        
    # tx_dict = workflow_temp.copy()
    # get_output(JSON_FILE_PATH, rm_dict)

    # # generate show result operator

    # # create the operator dict
    # for operator in rm_dict["operator"]:
    #     op_type = mapping_table[operator["@class"]]
    #     og = OperatorGenerator(op_type, operator)
    #     tx_dict["operators"].append(og.get_temp())
    #     tx_dict["operatorPositions"][og.get_id()] = og.generate_pos()
    # # get operator position
    # get_output(CURRENT_OUTPUT, tx_dict)
    # get connects



    # generate tx_dict
    # for operator in rm_dict["operator"]:
    #     print(operator)
        # if operator["@class"] in mapping_table:

    


if __name__ == "__main__":
    main()