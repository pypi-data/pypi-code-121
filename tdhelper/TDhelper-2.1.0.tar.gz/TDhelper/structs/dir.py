import json

class linked_list:
    '''
    链表
    '''
    def __init__(self, resource: any):
        self.__key= None
        self.__expand_resource= resource
        self.__nodes=[]

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key= value
    
    @property
    def expand_resource(self):
        return self.__expand_resource
    
    @property
    def nodes(self):
        return self.__nodes
    
    def find(self, find_value:any):
        '''
        查找元素

        - Parameters:
            find_value: 您需要查找的值, 搜索范围(pk_field).
        '''
        # 如果KEY与查找值一致返回对象本身
        if self.__key == find_value:
            return self
        for item in self.__nodes:
            # 进入下级查找
            result= item.find(find_value)
            if result:
                return result
        return None
    
    def toJson(self):
        '''
        cls<node> to json str formatter
        '''
        json_templete= '"{}":&lt;"expand":&lt;{}&gt;,"nodes":['
        ret= json_templete.format(self.__key, self.__getExpand_str())
        if self.__nodes:
            v_count= 1
            for item in self.__nodes:
                str_ret= ''
                str_ret+= item.toJson()
                if v_count < len(self.__nodes):
                    str_ret+= ","
                ret+= "{"+str_ret+"}"
                if v_count < len(self.__nodes):
                    ret+= ","
                v_count+= 1

            ret+= "]}"
        else:
            ret+= "]}"
        return ret
    
    def __getExpand_str(self):
        '''
        generate json's expand  value.
        '''
        ret_str= ''
        v_pos= 0
        for item in self.__expand_resource.__dict__:
            if v_pos > 0:
                ret_str+= ', '
            if isinstance(self.__expand_resource.__dict__[item], str):
                ret_str+= '"'+ str(item) +'" : "' + str(self.__expand_resource.__dict__[item]) + '"'
            else:
                ret_str+= '"'+ str(item) +'" : ' + str(self.__expand_resource.__dict__[item])
            v_pos+= 1
        return ret_str

class Directory:
    '''
    目录结构
    '''
    def __init__(self, pk_field: str, parent_field: str):
        '''
        init

        - Parameters:
            pk_field: 索引字段, cls<string>
            parent_field: 关联索引的字段, cls<string>
        '''
        self.__nodes= []
        self.__pk_field= pk_field
        self.__parent_field= parent_field
    
    def append(self, node: linked_list):
        '''
        增加一个节点
        
        - Parameters:
            node: 节点对象, cls<linked_list> 
        '''
        if node:
            if hasattr(node.expand_resource, self.__pk_field):
                node.key= getattr(node.expand_resource, self.__pk_field)
                if hasattr(node.expand_resource, self.__parent_field):
                    find_value= getattr(node.expand_resource, self.__parent_field)
                    if bool(find_value):
                        for item in self.__nodes:
                            find_ret= item.find(find_value)
                            if find_ret:
                                find_ret.nodes.append(node)
                                return True
                        return False
                    else:
                        self.__nodes.append(node)
                        return True
                else:
                    raise Exception(self.__parent_field + ' can not found.')
            else:
                raise Exception(self.__pk_field + ' can not found.')
        else:
            raise Exception('node is null.')

    def toJson(self):
        '''
        json字符串

        - Returns:
            cls<str>
        '''
        ret= ""
        v_count=1
        for item in self.__nodes:
            ret+= item.toJson() 
            if v_count < len(self.__nodes):
                ret+= ","
            v_count+= 1
        ret= ret.replace('&lt;', '{')
        ret= ret.replace('&gt;', '}')
        ret= ret.replace(',}',"}")
        return "{"+ret+"}"

    def toSerialize(self):
        '''
        序列化

        - Returns:
            cls<dict>
        '''
        return json.loads(self.toJson)