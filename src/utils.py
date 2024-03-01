def format_dict(xml_dict: dict, ret_dict: dict) -> None:
    """
        Further process the parse Knime workflow dictionary to make the keys and values more meaningful
    """
    if "entry" in xml_dict:
        if isinstance(xml_dict["entry"], list):
            for entry in xml_dict["entry"]:
                ret_dict[entry["@key"]] = entry["@value"]
        else:
            ret_dict[xml_dict["entry"]["@key"]] = xml_dict["entry"]["@value"]
    if "config" in xml_dict:
        if isinstance(xml_dict["config"], list):
            for config in xml_dict["config"]:
                ret_dict[config["@key"]] = {}
                format_dict(config, ret_dict[config["@key"]])
        else:
            ret_dict[xml_dict["config"]["@key"]] = {}
            format_dict(xml_dict["config"],
                        ret_dict[xml_dict["config"]["@key"]])
    return
