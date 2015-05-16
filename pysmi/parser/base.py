
class AbstractParser(object):
    def reset(self):
        raise NotImplementedError()

    def parse(self, data, **kwargs):
        raise NotImplementedError()
