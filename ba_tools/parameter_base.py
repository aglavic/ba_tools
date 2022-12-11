"""
Base class used for model items that have parameters with physical units associated to them.
"""

from dataclasses import dataclass, fields, field, Field

from bornagain import millimeter as mm, nm, nm2, angstrom, deg, rad

SUPPORTED_UNITS = {
    'nm': nm,
    'nm²': nm2,
    'nm2': nm2,
    'mm': mm,
    'm': 1000.*mm,
    'angstrom': angstrom,
    'deg': deg,
    'rad': rad,
    }

def pp(default, unit, unit_value=None):
    # Physical parameter field with unit to be converted to
    return field(default=default, metadata={'unit': unit, 'unit_value': unit_value})

@dataclass
class Parametered:
    """
    Base class for all instruments.

    Constructor should include all necessary instrument parameters.
    """

    def _get_unit_value(self, fi: Field):
        unit = fi.metadata['unit']
        if fi.metadata.get('unit_value', None) is not None:
            return fi.metadata['unit_value']
        else:
            return SUPPORTED_UNITS[unit]

    def __post_init__(self):
        """
        Perform unit transformation in case the class defines units
        on it's fields via metadata.
        """
        for fi in fields(self):
            if fi.metadata.get('unit', None) is not None:
                unit_value = self._get_unit_value(fi)
                setattr(self, fi.name, getattr(self, fi.name)*unit_value)

    def __repr__(self):
        return self._repr_pretty_()

    def _repr_pretty_(self):
        """
        Representation that includes units and transforms the parameters back.
        For use in IPython.
        """
        output=self.__class__.__qualname__+f"("
        field_strings=[]
        for fi in fields(self):
            if fi.metadata.get('unit', None) is not None:
                unit = fi.metadata['unit']
                unit_value = self._get_unit_value(fi)
                value = getattr(self, fi.name)/unit_value
                field_strings.append(f"{fi.name}={value:.4g} {unit}")
            else:
                field_strings.append(f"{fi.name}={getattr(self, fi.name)!r}")

        output+=', '.join(field_strings)
        output+=")"
        return output
