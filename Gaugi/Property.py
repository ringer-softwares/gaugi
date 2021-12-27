

__all__ = ["declareProperty", "get_property"]

#
#TODO shoul implement protected and private dynamic members
#
def declareProperty( self, kw, name, value, private=False, protected=False):
    attribute = name
    if not name in kw.keys():
        setattr(self, attribute, value)
    else:
        setattr(self, attribute, kw[name])



def get_property( kw, name, value = None ):
  """
  Use together with None to have only one default value for your job
  properties.
  """
  if not name in kw:
    kw[name] = value
  return kw[name]
