from yaml import load, CLoader as Loader, dump, CDumper as Dumper

def get_yaml(fp):
    with open(fp, 'r') as yaml_file:
        return load(yaml_file.read(), Loader=Loader)

def save_as_yaml(fp, data):
    with open(fp, 'w') as yaml_file:
        yaml_file.write(dump(data, Dumper=Dumper))
