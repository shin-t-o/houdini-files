import numpy as np
import pandas as pd
import unicodedata as ud
import psycopg2
import houpandas as hp


node = hou.pwd()
geo = node.geometry()

# ======================
# general function
# ======================
def can_start_to_process() -> bool:
    return (
        hou.ch("../datasource")!="default_val" and
        hou.ch("../store_data_in")!="default_val"
    )

def check_columns_is_valid(columns: list) -> bool:
    for col in columns:
        if ud.east_asian_width(col[0])!="Na":
            return False
    return True


# ======================
# data extractors
# ======================
# select nothing
def return_default():
    return None

# PostgreSQL
def get_conn(conf: dict):
    return psycopg2.connect(**conf)

def get_blank_flg(conf: dict) -> bool:
    """ 設定情報が全て埋まっていればTrue / それ以外はFalse
    """
    return np.array(conf.values()!="").all()

def read_postgres() -> pd.DataFrame:
    """ PostgreSQL実行用
    """
    conn_conf: dict = {
        "host": hou.ch("../host"),
        "port": hou.ch("../port"),
        "dbname": hou.ch("../dbname"),
        "user": hou.ch("../user"),
        "password": hou.ch("../password"),
    }

    _flg = get_blank_flg(conf=conn_conf)

    # host, port, ... の各設定箇所に値が入ると接続処理開始
    if _flg:
        _conn = get_conn(conf=conn_conf)
        return pd.read_sql(
            sql="SELECT * FROM " + hou.ch("../postgres_table") + " limit" + str(hou.ch("../data_size")) + ";",
            con=_conn
            )
    else:
        return None

# CSV File
def read_csv() -> pd.DataFrame:
    return pd.read_csv(
        hou.ch("../csv_filepath"),
        skiprows=hou.ch("../csv_skiprows"),
        encoding="utf-8",
        # header=None,

    )


# Excel File
def read_excel() -> pd.DataFrame:
    return pd.read_excel(
        hou.ch("../excel_filepath"),
        sheet_name=hou.ch("../excel_sheetname"),
        skiprows=hou.ch("../excel_skiprows"),
        # nrows=hou.ch("../excel_nrows"),
        # header=None,
    )

# ======================
# composite functions
# ======================
# "Data Source" selector -> return dataframe
def get_datasource(source: str):
    switcher: dict = {
        "default_val": return_default,
        "postgresql": read_postgres,
        "csv_file": read_csv,
        "excel_file": read_excel
    }
    return switcher[source]

# check dataframe before return
def data_checker(df: pd.DataFrame) -> pd.DataFrame:
    """ 後続処理に渡す前に諸々チェック

    1. カラム名がアルファベットのみでなければエラー終了
    2. カラム名が大文字の場合小文字に変換

    処理追加時はこの関数内に追加

    """
    # 1.
    if not check_columns_is_valid(df.columns):
        raise AttributeError("Columns must be alphabets.")

    # 2.
    df.rename(columns=str.lower, inplace=True)

    return df

# ======================
# MAIN part
# ======================
if can_start_to_process():
    # check dataframe before make attributes
    raw_df: pd.DataFrame = data_checker(
        # data extract -> filter df size
        df=get_datasource(source=hou.ch("../datasource"))()[: hou.ch("../data_size")]
    )

    # select data store type
    if hou.ch("../store_data_in")=="in_attributes":
        # dataframe -> houdataframe
        df: hp.HouDataFrame = hp.HouDataFrame(raw_df)
        # houdataframe -> houdini attributes
        df.to_geometry(geo)
        print("set attributes from data source.")
    elif hou.ch("../store_data_in")=="in_df_cache":
        # dataframe -> session cache data
        cache_node = hou.node("../..")
        cache_node.setCachedUserData(hou.node("../").name(), raw_df)
        print("set cachedUserData from data source.")
