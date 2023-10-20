import json
import xmltodict
from pprint import pprint
from knime_operator_generator import OperatorGenerator
import re
import uuid

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

def generate_link(mapping, connection):

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
    # template[]
    sourceID = connection['entry'][0]['@value']
    sourcePort = int(connection['entry'][2]['@value'])
    destID = connection['entry'][1]['@value']
    destPort = int(connection['entry'][3]['@value'])
    template["source"]["operatorID"] = mapping[sourceID]
    template["source"]["portID"] = "output-" + str(sourcePort - 1)
    template["target"]["operatorID"] = mapping[destID]
    template["target"]["portID"] = "input-" + str(destPort - 1)
    
    return template

def main():
    # parse xml
    kn_dict = read_xml(XML_FILE_PATH)
    tx_dict = workflow_temp.copy()
    k2t_mapping = {}
    # pprint(kn_dict)
    kn_ops = kn_dict[2]["config"]
    # pprint(kn_ops)
    # parsing the operator part
    for op in kn_ops:
        # pprint(op)

        op_type = remove_pattern(op['entry'][1]['@value'])
        og = OperatorGenerator(op_type, op)
        # pprint(op)
        tx_dict["operators"].append(og.get_temp())
        tx_dict["operatorPositions"][og.get_id()] = og.generate_pos()
        k2t_mapping[op["entry"][0]["@value"]] = og.get_id()
    # parsing the connection part
    
    # print(k2t_mapping)
    # pprint(kn_dict[-1])
    # pprint(generate_link())
    connections = kn_dict[-1]['config']
    if type(connections) != list:
        connections = [connections]
    # pprint(connections)
    for connection in connections:
        tx_dict["links"].append(generate_link(k2t_mapping, connection))

    get_output(CURRENT_OUTPUT, tx_dict)
    
        # tx_dict["operatorPositions"][og.get_id()] = og.generate_pos()


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