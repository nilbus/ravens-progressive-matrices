class FigureObjectSet:
    def __init__(self, objects_dict):
        self.objects_dict = objects_dict

    def __repr__(self):
        return "<FigureObjectSet %s>" % (self.objects_dict.keys(),)

    def __getitem__(self, key):
        return self.objects_dict[key]

    def get(self, key, default):
        return self.objects_dict.get(key, default)

    def objects(self):
        return self.objects_dict.values()
