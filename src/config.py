from json import load

def load_config(config_path, resources_path):
    """
    Parses and returns the config files

    Returns: (dict, dict) <config, resources_cfg>
    """
    config = {}
    with open(config_path) as j:
        config = load(j)

    resources_cfg = {}
    # setup config
    with open(resources_path) as j:
        resources_cfg = load(j)

    return config, resources_cfg
