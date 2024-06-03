import yaml

def read_yaml(config_file: str):
    print(f"Reading {config_file} file")
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
        return config
