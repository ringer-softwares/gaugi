

__all__ = ["declareProperty", "get_property"]


def declareProperty( self, kw, name, value, private=False, protected=False):
    # private
    attribute = ('__' + name ) if private else name
    # protected
    attribute = ('_' + name ) if protected else name
    if not name in kw:
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
