import pathlib
import sys

import jinja2


def get_template(template_name):
    TEMPLATES_PATH = pathlib.Path(__file__).resolve().parent / "templates"
    loader = jinja2.FileSystemLoader(searchpath=TEMPLATES_PATH)
    env = jinja2.Environment(loader=loader)
    return env.get_template(template_name)


def render_template(template_name, data=None):
    template = get_template(template_name)
    return template.render(data=data)


def parse_tfvars_file(file_path):
    variables = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                variables[key.strip()] = value.strip().strip('"')
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

    common_keys = set(variables_list[0].keys())
    for variables in variables_list[1:]:
        common_keys &= set(variables.keys())

    common_values = {}
    differences = {}
    for key in common_keys:
        values = [
            (variables[key], str(tfvars_file))
            for variables, tfvars_file in zip(variables_list, tfvars_files)
        ]
        unique_values = set(value for value, _ in values)
        common_values[key] = values[0][0] if len(unique_values) == 1 else None

        if len(unique_values) > 1:
            differences[key] = values

    print("Common values:")
    max_key_width = max(len(key) for key in common_values.keys())
    for key in sorted(common_values.keys()):
        value = common_values[key]
        if value is not None:
            print(f"{key:<{max_key_width}} = {value}")

    print()

    if differences:
        print("Differences:")
        for key, values in differences.items():
            print(f"Variable: {key}")
            sorted_values = sorted(values, key=lambda x: x[0])
            for value, file in sorted_values:
                print(f"  {file}: {key} = {value}")
            print()

    return 0
