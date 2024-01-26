"""
    This module can help you write lambda function and convert it into json string format
"""
import json
# write your code into the code string and execute the module
code_string = '''
if $values[0] in ["UTF-8", "UTF-16", "US-ASCII"]:
    ret = $values[0].replace("-","_")
else:
    ret = "UTF_8"
'''

# Convert the string to a JSON-serialized format
json_string = json.dumps(code_string)
print(json_string)
# copy the output in the terminal to your json file
