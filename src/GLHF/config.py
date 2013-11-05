import ConfigParser


class Config(object):
    
    VALUE_TYPE_MAPPING = {"str": str,
                          "int": int,
                          "hexstr": eval}
    
    def __init__(self):
        self.killed = False
    
    @staticmethod
    def fromFile(filePath):
        """
        Read the .cfg file to populate the config structure
        
        The .cfg file's syntax is:
        
        [$var_name]
        value = $var_value
        type = $var_type
        
        This function needs to convert the var_value to the expected var_type
        """
        parser = ConfigParser.ConfigParser()
        parser.read(filePath)
        cfg = Config()
        for varName in parser.sections():
            varValue = parser.get(varName, "value")
            varType = parser.get(varName, "type")
            varRealValue = Config.VALUE_TYPE_MAPPING[varType](varValue)
            setattr(cfg, varName, varRealValue)
        return cfg
    
