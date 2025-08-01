
import ast
import json5
import json

def loadConfig(path, fileName):

    # print('loadConfig os cwd::{}'.format(os.getcwd()))
    config_file = open(path + fileName, "rt", encoding="UTF8")
    ds = config_file.read()
    json_data = ast.literal_eval(json.dumps(ds))
    configData = json5.loads(json_data)
    config_file.close()
    return configData
