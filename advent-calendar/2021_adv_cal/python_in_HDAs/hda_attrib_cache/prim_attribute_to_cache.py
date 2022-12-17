import numpy as np
import pandas as pd

node = hou.pwd()
geo = node.geometry()


cols: list = []
dfs: list = []
prefix: list = ["_x", "_y", "_z", "_w"]

# make "columns" list for dataframe
for attr in geo.primAttribs():
    cols.append(attr.name())


if len(cols)>0:
    for col in cols:
        _vals: list = []
        # attribute copy per prim
        for prim in geo.prims():
            _vals.append(prim.attribValue(col))
        dfs.append(pd.DataFrame(data=_vals, columns=[col]))

    # partial dataframes -[concat]-> 1 dataframe
    df: pd.DataFrame = pd.concat(dfs, axis=1)
    # dataframe -> session cache data
    cache_node = hou.node("../..")
    cache_node.setCachedUserData(hou.node("../").name()+"_prim", df)
    print("set cachedUserData from primitive attributes.")
