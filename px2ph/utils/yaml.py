from yaml import load, CLoader as Loader

def get_yaml(fp):
    with open(fp, 'r') as yaml_file:
        return load(yaml_file.read(), Loader=Loader)
