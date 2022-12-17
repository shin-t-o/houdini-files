def has_attrib(geo: hou.Geometry, attr: str) -> bool:
    return not (
        (geo.findPointAttrib(attr) is None)
        & (geo.findVertexAttrib(attr) is None)
        & (geo.findPrimAttrib(attr) is None)
        & (geo.findGlobalAttrib(attr) is None)
    )


def filter_nodes_by_attribute(source_sop: list[hou.SopNode], attr: str) -> list[str]:
    """
    sourece_sopノード群のうち、attrを含むノードのみ抽出して返却

    Args:
        source_sop: 検索元SopNodeリスト
        attr: 抽出条件attribute

    Returns:
        filtered_sop: 抽出後のノード名リスト
    """
    filtered_sop: list[hou.SopNode] = []
    for source in source_sop:
        try:
            if has_attrib(source.geometry(), attr):
                filtered_sop.append(source)
        except AttributeError:
            continue

    # こっちの名前のがいいかもしれん
    # return source_sop
    return remove_downstream_nodes(filtered_sop)
    # return [ x.name() for x in geo_list if x.name() not in source_candidate ]


def remove_downstream_nodes(source_sop: list[hou.SopNode]) -> list[hou.SopNode]:
    """ノード群に於いて下流に当たるノードを除外

    source_sopノード群のうち「ワイヤーで繋がっているもの」を探索しその最上流以外を除去する
    独立したノード群を受け取っても変更操作はしない

    Args:
        source_sop: フィルタ適用前SopNodeリスト

    Returns:
        filtered_sop: フィルタ適用後SopNodeリスト
    """
    filtered_sop: list[hou.SopNode] = []
    source_list: list[str] = [x.name() for x in source_sop]

    for sop in source_sop:
        input_list: list[str] = [x.name() for x in sop.inputs()]
        # sopノードのinputもsource_sopノード群にいる = 除外対象
        #  / sopノードのinputがsource_sopノード群に居ない = 抽出対象
        # if not (set(input_list) - set(["object_merge"])) & set(source_list):
        if not (set(input_list)) & set(source_list):
            filtered_sop.append(sop)

    return filtered_sop


def filter_nodes_by_input(source_sop: list[hou.SopNode], attr: str) -> list[hou.SopNode]:
    """
    SopNodeリストの中で「そのinputがtarget_attrを持たないノード」のみを抽出する

    Args:
        source_sop: 元となるSopNodeリスト

    Returns:

    """
    filtered_sop: list[hou.SopNode] = []

    for sop in source_sop:
        # try:
        inputs: list[hou.SopNode] = list(sop.inputs())
        for input in inputs:
            if attr not in get_attr_list(input.geometry()):
                filtered_sop.append(sop)
                break
        #
        # except AttributeError:
        #     continue

    return filtered_sop


def get_node_name_from_sop_list(sop_list: list[hou.SopNode]) -> list[str]:
    result: list[str] = []

    for sop in sop_list:
        result.append(sop.name())

    return result


# -------------------------------------------------
# 設定部分
# -------------------------------------------------
# 調査したい範囲の親ノードを定義
settings: dict = {
    # "root_dir": "/obj/WORK/",
    # 探したいattributeを定義
    "target_attr": "pAttr",
    # ノードの何番目までを調べるか
    # "search_index_num": 1,
}

# -------------------------------------------------
# 実行部分
# -------------------------------------------------
# 別にmainで括る必要もないのだが見栄え的に
def main(settings: dict):
    # 繋いだノードの「子孫（＝上流ノード）」を候補として取得
    # base_sop: list[hou.SopNode] = hou.pwd().inputAncestors()
    parent_dir: str = hou.pwd().path().replace("/" + hou.pwd().name(), "")
    base_sop: list[hou.SopNode] = hou.node(parent_dir).children()
    # 指定の条件でfilter処理を実行
    source_sop = filter_nodes_by_attribute(source_sop=base_sop, attr=settings["target_attr"])
    # result_sop = filter_nodes_by_input(source_sop=source_sop, attr=settings["target_attr"])
    result_sop = source_sop

    print(" ============================= ")
    # [1] 候補を出力したい場合はこっち
    print("result_sop: ", get_node_name_from_sop_list(sop_list=result_sop))
    # [2] 候補となるノードを選択状態 + Template Flag ONにしたい場合はこっち
    for sop in result_sop:
        sop.setSelected(True)
        sop.setTemplateFlag(True)


main(settings=settings)
