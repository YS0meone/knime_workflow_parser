"""
    This module can help you write lambda function and convert it into json string format
"""
import json
# write your code into the code string and execute the module
code_string = '''
ret = []
for i in range(0, len($values), 3):
    group = {}
    group["aggFunction"] = $values[i].lower()
    group["result attribute"] = $values[i + 1]
    group["attribute"] = $values[i + 2]
    ret.append(group)
'''

# Convert the string to a JSON-serialized format
json_string = json.dumps(code_string)
print(json_string)
# copy the output in the terminal to your json file
