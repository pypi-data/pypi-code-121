
def existsString(targetString:str, matchingString:list):
    
    """
    対象文字列にマッチング文字列リストの要素が含まれるか判定する

    Parameters
    ----------
    targetString : str
        対象文字列
    matchingString : list
        マッチング文字列リスト
    """
    
    # 文字列のマッチング
    for s in matchingString:
        result = s in targetString
        if result:
            break
    
    return result

def getMatchedStringList(targetString:str, matchingString:list):
    
    """
    対象文字列に対してマッチング文字列リストと一致した要素を返す

    Parameters
    ----------
    targetString : str
        対象文字列
    matchingString : list
        マッチング文字列リスト
    """
    
    result = []
    
    # 文字列のマッチング
    for s in matchingString:
        if s in targetString:
            result.append(s)
    
    return result
    