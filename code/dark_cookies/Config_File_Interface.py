from os.path import exists

class Config_File():
    def __init__(self, filename) -> None:
        self.filename = filename
        if not exists(filename):
            with open(filename, 'w'):
                pass

    def get_values(self):
        values = dict()
        with open(self.filename, 'r') as fp:
            for line in fp.readlines():
                line_values = line.split("=")
                if len(line_values) == 2:
                    values[line_values[0]] = str(line_values[1]).rstrip()
        return values

    def get_value(self, key):
        values = self.get_values()
        if key in values:
            return str(values[key])
        return None

    def add_value(self, key, value):
        values = self.get_values()
        values[key] = value
        self.write_values_to_file(values)
        
    def add_values(self, values):
        for v in values:
            self.add_value(v, values[v])

    def write_values_to_file(self, values):
        with open(self.filename, 'w') as fp:
            fp.writelines([str(v) + "=" + str(values[v]).rstrip() + "\n" for v in values])
                
    def remove_value(self, key):
        values = self.get_values()
        values.pop(key)
        self.write_values_to_file(values)

    def remove_all_values(self):
        values = {}
        self.write_values_to_file(values)