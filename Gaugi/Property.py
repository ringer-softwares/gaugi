

__all__ = ["declareProperty", "get_property"]


def declareProperty( self, kw, key, value):
    if not key in kw or kw[key] is None:
        setattr(self, key, value)
    else:
        setattr(self, key, kw[key])
        kw.pop(key)



def get_property( kw, key, default = None ):
  """
  Use together with None to have only one default value for your job
  properties.
  """
  if not key in kw or kw[key] is None:
    kw[key] = default
  return kw.pop(key)
