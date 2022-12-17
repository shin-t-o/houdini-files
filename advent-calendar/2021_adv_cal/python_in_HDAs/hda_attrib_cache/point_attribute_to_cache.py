import numpy as np
import pandas as pd

node = hou.pwd()
geo = node.geometry()


cols: list = []
dfs: list = []
prefix: list = ["_x", "_y", "_z", "_w"]

# make "columns" list for dataframe
for attr in geo.pointAttribs():
    cols.append(attr.name())

for col in cols:
    _vals: list = []
    _type: str = type(geo.points()[0].attribValue(col))

    # attribute: ['P'](= P[x], P[y], P[z]) -> df columns: P_x, P_y, P_z
    if _type is tuple:
        _size: int = len(geo.points()[0].attribValue(col))
        df_col: list = [ col+prefix[i] for i in range(_size) ]
    else:
        df_col: list = [col]

    # attribute copy per point
    for point in geo.points():
        _vals.append(point.attribValue(col))
    dfs.append(pd.DataFrame(data=_vals, columns=df_col))

# partial dataframes -[concat]-> 1 dataframe
df: pd.DataFrame = pd.concat(dfs, axis=1)
# dataframe -> session cache data
cache_node = hou.node("../..")
cache_node.setCachedUserData(hou.node("../").name()+"_point", df)
print("set cachedUserData from point attributes.")