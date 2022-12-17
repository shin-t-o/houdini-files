def has_attrib(geo: hou.Geometry, attr: str) -> bool:
    """
    ジオメトリの指定attribute保持有無を返却
    """
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

    return remove_downstream_nodes(filtered_sop)


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
        if not set(input_list) & set(source_list):
            filtered_sop.append(sop)

    return filtered_sop


def get_node_name_from_sop_list(sop_list: list[hou.SopNode]) -> list[str]:
    """
    SopNodeリストを受け取り、その名称（str）のリストにして返却
    """
    result: list[str] = []

    for sop in sop_list:
        result.append(sop.name())

    return result


# -------------------------------------------------
# 設定部分
# -------------------------------------------------
# scope: str = "upstream_only"
scope: str = "current_dir"
# 探したいattributeを定義
target_attr: str = "pAttr"


# -------------------------------------------------
# 実行部分
# -------------------------------------------------
def exec_search(scope: str, target_attribute: str):
    # 既存のTemplateフラグを除去
    parent_dir: str = hou.pwd().path().replace("/" + hou.pwd().name(), "")
    current_sop: list[hou.SopNode] = hou.node(parent_dir).children()
    for sop in current_sop:
        sop.setTemplateFlag(False)

    if scope == "upstream_only":
        # 繋いだノードの「子孫（＝上流ノード）」を候補として取得
        base_sop: list[hou.SopNode] = hou.pwd().inputAncestors()
    elif scope == "current_dir":
        base_sop: list[hou.SopNode] = current_sop

    # 指定の条件でfilter処理を実行
    result_sop = filter_nodes_by_attribute(source_sop=base_sop, attr=target_attribute)

    # print(" ============================= ")
    # [1] 候補を出力したい場合はこっち
    # print("result_sop: ", get_node_name_from_sop_list(sop_list=result_sop))
    # [2] 候補となるノードを選択状態 + Template Flag ONにしたい場合はこっち
    if len(result_sop) == 0:
        print("Node not found.")
    else:
        for sop in result_sop:
            sop.setSelected(True)
            sop.setTemplateFlag(True)


exec_search(scope=scope, target_attribute=target_attr)
