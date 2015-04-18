# Package exception model:
# Here we subclass base Python exception overriding its constructor to
# accomodate error message string as its first parameter and an open
# set of keyword arguments that become exception object attributes.
# While exception object is bubbling up the call stack, intermediate
# exception handlers may insert their own attributes into exception
# object.

class PySmiError(Exception):
    def __init__(self, *args, **kwargs):
        self.message = args and args[0] or ''
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(['%s=%r' % (k, getattr(self, k)) for k in dir(self) if k[0] != '_' and k != 'args']))

    def __str__(self):
        return self.message

class PySmiLexerError(PySmiError): pass

class PySmiParserError(PySmiLexerError): pass
class PySmiSyntaxError(PySmiParserError): pass

class PySmiSearcherError(PySmiError): pass
class PySmiSourceNotModifiedError(PySmiSearcherError): pass

class PySmiReaderError(PySmiError): pass
class PySmiSourceNotFoundError(PySmiReaderError): pass

class PySmiCodegenError(PySmiError): pass
class PySmiSemanticError(PySmiCodegenError): pass

class PySmiWriterError(PySmiError): pass
