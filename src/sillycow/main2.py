import pathlib
import sys


def parse_tfvars_file(file_path):
    variables = {}
    with open(file_path, "r") as file:
        in_multiline_comment = False
        for line in file:
            line = line.strip()
            if not in_multiline_comment:
                if line.startswith("/*"):
                    in_multiline_comment = True
                    continue
                elif line.startswith("#") or line.startswith("//"):
                    continue
                elif "=" in line:
                    key, value = line.split("=", 1)
                    variables[key.strip()] = value.strip().strip('"')
            else:
                if line.endswith("*/"):
                    in_multiline_comment = False
    return variables


def compare_tfvars_files(base_dir):
    base_path = pathlib.Path(base_dir)
    tfvars_files = list(base_path.glob("*.tfvars"))

    if len(tfvars_files) < 2:
        print(
            "At least two .tfvars files are required for comparison.", file=sys.stderr
        )
        return 1

    variables_list = []
    for tfvars_file in tfvars_files:
        variables = parse_tfvars_file(tfvars_file)
        variables_list.append(variables)

    all_keys = set().union(*[variables.keys() for variables in variables_list])

    common_values = {}
    differences = {}
    variable_status = {}

    for key in all_keys:
        values = [
            (variables.get(key, None), str(tfvars_file))
            for variables, tfvars_file in zip(variables_list, tfvars_files)
        ]
        unique_values = set(value for value, _ in values if value is not None)

        if all(value is not None for value, _ in values):
            if len(unique_values) == 1:
                common_values[key] = unique_values.pop()
            else:
                differences[key] = values
        else:
            missing_files = [file for value, file in values if value is None]
            present_files = [
                (file, value) for value, file in values if value is not None
            ]
            variable_status[key] = {"missing": missing_files, "present": present_files}

    if common_values:
        print("Common values:")
        max_key_width = max(len(key) for key in common_values.keys())
        for key in sorted(common_values.keys()):
            value = common_values[key]
            print(f"{key:<{max_key_width}} = {value}")
        print()

    if differences:
        print("Differences:")
        for key, values in differences.items():
            print(f"Variable: {key}")
            sorted_values = sorted(values, key=lambda x: x[0] or "")
            for value, file in sorted_values:
                if value is not None:
                    print(f"  {file}: {key} = {value}")
            print()

    if variable_status:
        print("Variable status:")
        for key, status in variable_status.items():
            print(f"Variable: {key}")
            for file in status["missing"]:
                print(f"  Missing in {file}")
            for file, value in status["present"]:
                print(f"  Present in {file} with value {value}")
            print()

    return 0
