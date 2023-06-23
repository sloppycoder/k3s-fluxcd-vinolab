import json
import os
import sys


def add_key_from_file(json_file, key, value_file):
    with open(value_file, "r") as f:
        value = "".join(f.readlines())

    with open(json_file, "r") as f:
        content = json.load(f)
        content[key] = value

    with open(json_file, "w") as f:
        json.dump(content, f, indent=4)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        script = os.path.basename(__file__)
        print("encode.py <json_file> <key_name> <file_for_key_content>")

    add_key_from_file(sys.argv[1], sys.argv[2], sys.argv[3])
