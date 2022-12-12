"""
Base class used for model items that have parameters with physical units associated to them.
"""

from dataclasses import Field, dataclass, field, fields

from bornagain import angstrom, deg
from bornagain import millimeter as mm
from bornagain import nm, nm2, rad

SUPPORTED_UNITS = {
    "nm": nm,
    "nm²": nm2,
    "nm2": nm2,
    "mm": mm,
    "m": 1000.0 * mm,
    "angstrom": angstrom,
    "deg": deg,
    "rad": rad,
}


def pp(default, unit, unit_value=None):
    # Physical parameter field with unit to be converted to
    return field(default=default, metadata={"unit": unit, "unit_value": unit_value})


@dataclass
class Parametered:
    """
    Base class for all dataclassess that hold physical parameters. Includes an
    automatic conversion with the correct unit (see function pp) and nice
    representations, especially for IPython notebook use.

    If a child class defines _repr_svg_, it will be included in the
    html table showing the parameters.
    """

    def _get_unit_value(self, fi: Field):
        unit = fi.metadata["unit"]
        if fi.metadata.get("unit_value", None) is not None:
            return fi.metadata["unit_value"]
        else:
            return SUPPORTED_UNITS[unit]

    def __post_init__(self):
        """
        Perform unit transformation in case the class defines units
        on it's fields via metadata.
        """
        for fi in fields(self):
            if fi.metadata.get("unit", None) is not None:
                unit_value = self._get_unit_value(fi)
                setattr(self, fi.name, getattr(self, fi.name) * unit_value)

    def __repr__(self):
        """
        Representation that includes units and transforms the parameters back.
        For use in IPython.
        """
        output = self.__class__.__qualname__ + "("
        field_strings = []
        units = []
        for fi in fields(self):
            if fi.metadata.get("unit", None) is not None:
                unit = fi.metadata["unit"]
                unit_value = self._get_unit_value(fi)
                value = getattr(self, fi.name) / unit_value
                field_strings.append(f"{fi.name}={value:.4g}")
                units.append(unit)
            else:
                field_strings.append(f"{fi.name}={getattr(self, fi.name)}")
                units.append("")

        output += ", ".join(field_strings)
        output += ")\n"
        unit_string = "# Units:"
        for fi in fields(self):
            sidx = output.find(f"{fi.name}=")
            if len(units) == 1:
                curidx = output.find(")", sidx)
            else:
                curidx = output.find(",", sidx)
            unit = units.pop(0)
            unit_string += " " * max(0, (curidx - len(unit_string) - len(unit)))
            unit_string += unit + ","
        output += unit_string[:-1]
        return output

    def _repr_html_(self):
        flds = list(fields(self))
        columns = max(5, len(flds))
        if hasattr(self, "_box_svg_"):
            svg_img = '<td rowspan="0">' + self._box_svg_() + "</td>"
            columns += 1
        else:
            svg_img = ""
        output = f'<table><tr><th colspan="{columns}" style="text-align: center;">{self.__class__.__qualname__}</th>'
        output += f"{svg_img}</tr>\n"

        output += "<tr>"
        for fi in flds[:5]:
            if fi.metadata.get("unit", None) is not None:
                unit = fi.metadata["unit"]
                output += f"<th>{fi.name}<br />({unit})</th>"
            else:
                output += f'<th style="vertical-align: middle;">{fi.name}</th>'
        output += "</tr>\n<tr>"

        for i, fi in enumerate(flds):
            value = getattr(self, fi.name)
            if fi.metadata.get("unit", None) is not None:
                unit_value = self._get_unit_value(fi)
                value /= unit_value
                field_string = f"{value:.4g}"
            else:
                field_string = f"{getattr(self, fi.name)}"
            output += f"<td>{field_string}</td>"
            if i % 5 == 4 and len(flds) > i:
                output += "</tr>\n<tr>"
                for fi in flds[i + 1 : i + 6]:
                    if fi.metadata.get("unit", None) is not None:
                        unit = fi.metadata["unit"]
                        output += f"<th>{fi.name}<br />({unit})</th>"
                    else:
                        output += f'<th style="vertical-align: middle;">{fi.name}</th>'
                output += "</tr>\n<tr>"
        output += "</tr></table>"
        return output
