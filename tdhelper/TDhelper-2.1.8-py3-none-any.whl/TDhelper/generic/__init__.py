
def printTable(table: []):
    '''
    表格化输出信息
    
    - 参数：
        - table: [],数组里请保存dict类型数据
    
    - 返回值:
        str
    '''
    if table:
        m_str=''
        keyheader = []
        tableWidth=[]
        for name in table[0].keys():
            keyheader.append(name)
        offset=0
        for item in table:
            for name,value in item.items():
                if offset < len(tableWidth):
                    if len(name)> tableWidth[offset]:
                        tableWidth[offset]=len(name)
                else:
                    tableWidth.append(len(name))
                if len(str(value))>tableWidth[offset]:
                    tableWidth[offset]= len(str(value))
                offset+=1
            offset=0
        offset = 0
        for header in keyheader:
            if offset == 0:
                m_str+="+"
            for i in range(0, tableWidth[offset]+10):
                m_str+="-"
            m_str+='+'
            offset += 1
        offset = 0
        m_str+='\r\n'
        for header in keyheader:
            m_str+='|'
            m_str+=' '+header
            for i in range(0, tableWidth[offset]+10-len(header)-1):
                m_str+=' '
            offset+=1
        m_str+='|'
        m_str+='\r\n'
        offset = 0
        for header in keyheader:
            if offset == 0:
                m_str+="+"
            for i in range(0, tableWidth[offset]+10):
                m_str+="-"
            offset+=1
            m_str+='+'
        m_str+='\r\n'
        offset=0
        for item in table:
            for name, value in item.items():
                m_str+='|'
                m_str+=' '+str(value)
                for i in range(0, tableWidth[offset]+10-len(str(value))-1):
                    m_str+=' '
                offset += 1
            m_str+='|'
            m_str+='\r\n'
            offset = 0
        offset=0
        for header in keyheader:
            if offset == 0:
                m_str+="+"
            for i in range(0, tableWidth[offset]+10):
                m_str+="-"
            offset+=1
            m_str+='+'
        m_str+='\r\n'
        return m_str
    return ''