from os import remove
from typing import Callable
import prettytable, json
from json2html import json2html


class _Create_Data(type):
    # Class modifier
    def __new__(self, class_name, bases, attributes):
        return type(class_name, (), attributes)


class DataFrame(metaclass=_Create_Data):
    data_list: list = []
    indexed:bool

    def __init__(self, data_list , sort_order:tuple|list|None=None  , **kwargs) -> None:
        self.indexed = kwargs.get("indexed"  , False)
        self.sort_order  = sort_order

        if not isinstance(data_list, list) : 
            raise TypeError("Invalid data_list type")     
        if not isinstance(sort_order , list) and sort_order is not None : 
            raise TypeError("Invalid sort_order !")

        if self.sort_order == None : 
            # print("Resorting to default sort !")
            self.sorted_order  = sorted
        else : 
            # print("Custom sort enabled !")
            self.sorted_order = self._create_sorter()

        self.data_list = data_list
        self.__add_items()
        self.__uinform_data_list()
        for key in self._item_keys:
            setattr(
                self,
                f"_{key}",
                type(
                    key,
                    (),
                    {
                        "__repr__": self._common_repr(key),
                        "__eq__": self._common_eq(key),
                        "__gt__": self._common_gt(key),
                        "__ge__": self._common_gte(key),
                        "__lt__": self._common_lt(key),
                        "__le__": self._common_lte(key),
                        "includes": self._common_op(key, "incl"),
                        "startswith": self._common_op(key, "strw"),
                        "endswith": self._common_op(key, "endw"),
                    },
                ),
            )
            setattr(self, key, self.__getattribute__("_" + key)())

    # Methods
    def to_list(self) -> str:
        return list(self.data_list)

    def to_json(self) -> str:
        li = list(self.data_list)
        li = json.dumps(li, indent=2)
        return li

    def to_html(self) -> str:
        li = self.to_json()
        li = json2html.convert(li)
        return li

    def to_csv(self) -> str:
        x = ",".join(self._item_keys)
        x += "\n"
        for item in self.data_list: 
            keys = ",".join([str(k).replace(","  , " ")for k in item.values()])
            x += f"{keys}\n"

        return x
        
    def export(self ,  file_name:str="output",format:str="json"  , directory:str="./") -> bool:
        file_url = f"{directory}/{file_name}.{format}"
        final = False
        with open( file_url, "w") as file :
            s = ""
            try:
                match format: 
                    case "json": 
                        s = self.to_json()      
                    case "csv":
                        s = self.to_csv()      
                    case "html":
                        s = self.to_html()      
                    case _ : 
                        raise Exception("Invalid file format")   

                file.write(s)    
                final = True
            except Exception as E:
                final = False

        if final == False : remove(file_url)
        return final

    # Dundder methods
    def __getitem__(self, item:str|tuple|int|slice) -> object:
        if  isinstance( item , tuple): 
            li = []
            z = []

            for x in self._item_keys:
                if x in item:
                    z += [x]

                    
            for x in self.data_list : 
                li.append({k : x[k] for k in x if k in z })

            return DataFrame(li , list(item) , indexed=self.indexed)

        if isinstance(item  , str):
            li = []
            z = None

            for x in self._item_keys:
                if x == item:
                    z = x

            for x in self.data_list : 
                for y in x: 
                    if y == z : 
                        li.append({k : x[k] for k in x if k == y })

            return DataFrame(li ,  None , indexed=self.indexed)

        if isinstance(item, self._dbool):
            count = 0
            current_list = []
            for index, ele in enumerate(item.tuple):
                if ele:
                    current_list.append(self.data_list[index])
                    count += 1

            return None if count == 0 else DataFrame([*current_list] , self.sort_order , indexed=self.indexed)

        li = self.data_list[item]
        if type(li) != list:
            return DataFrame([li] , self.sort_order , indexed=self.indexed)
        else:
            return DataFrame(li , self.sort_order)

    def __repr__(self) -> str:
        x = prettytable.PrettyTable()
        
        x.field_names = [ " ", *self._item_keys]  if self.indexed else self._item_keys
        for index , z in enumerate(self.data_list):
            z = [*z.values()]
            for i, y in enumerate(z):
                if len(str(y)) > 18:
                    z[i] = f"{y[:17]}..."
            x.add_row([index , *z] if self.indexed else [*z])

        return f"{x}\n_dtype : Dataframe_object"

    # Super Private methods
    def __add_items(self) -> None:
        """
        Returns all the possible stub heads
        """
        stub_heads = []

        for item in self.data_list:
            for x in item.keys():
                if x not in stub_heads:
                    stub_heads.append(x)

        self._item_keys = stub_heads
        self._item_keys = self.sorted_order(stub_heads)

    def __uinform_data_list(self) -> None: 
        """
        Modifies the data_list to make it uniform.
        NOTE : attributes with no values or if they dont exist then None will be assigned by default.

        eg .
            [{
                "id" : "_id",
                "_v" : "value",
            },
            {
                "id" : "_id"
            }]

        Here the sencond dict will be assigned a "_v" attribute with a default of None
        """
        
        for  i , item in enumerate(self.data_list):
            for x in self._item_keys:
                if item.get(x, False) == False:
                    item[x] = None

            self.data_list[i] =  { key : item[key] for key in  self.sorted_order(self.data_list[i])}
            
    # Private methods
    def _create_sorter(self):
        def sorter(li): 
            if isinstance(li , dict):
                li = list(li.keys())
            elif isinstance(li , list) : 
                pass
            else : 
                raise Exception("Invalid Type passed as sorter!")  
             
            li = self.sort_order

            z = []
            for x in  self._item_keys :  
                if x not in li: 
                    z.append(x)   
                z = sorted(z)

            li += z

            return tuple(li)
        return sorter    

    # Run time subclass methods generators
    def _common_repr(self, key:str) -> Callable:
        """
        Defines the __repr__ for the subclass object generated on the fly or at run time
        """

        def custom_repr(_self):
            x = prettytable.PrettyTable()
            x.field_names = ["index", key]

            for i, z in enumerate(self.data_list):
                for k, v in z.items():
                    if k == key:
                        if len(str(v)) > 18:
                            v = f"{v[:20]}..."
                        x.add_row([i, v])

            return f"{x}\n_dtype : DataFrame_attr({key})"

        return custom_repr

    def _common_eq(self, key:str) -> Callable:
        """
        Defines the __eq__ for the subclass object generated on the fly or at run time
        """

        def common_eq(_self, val):
            dbool = self._dbool(self.data_list, key, val, "eq")
            return dbool

        return common_eq

    def _common_gt(self, key:str) -> Callable:
        """
        Defines the __gt__ for the subclass object generated on the fly or at run time
        """

        def common_gt(_self, val):
            dbool = self._dbool(self.data_list, key, val, "gt")
            return dbool

        return common_gt

    def _common_gte(self, key:str) -> Callable:
        """
        Defines the __gt__ for the subclass object generated on the fly or at run time
        """

        def common_gte(_self, val):
            dbool = self._dbool(self.data_list, key, val, "gte")
            return dbool

        return common_gte

    def _common_lt(self, key:str) -> Callable:
        """
        Defines the __gt__ for the subclass object generated on the fly or at run time
        """

        def common_lt(_self, val):
            dbool = self._dbool(self.data_list, key, val, "lt")
            return dbool

        return common_lt

    def _common_lte(self, key:str) -> Callable:
        """
        Defines the __gt__ for the subclass object generated on the fly or at run time
        """

        def common_lte(_self, val):
            dbool = self._dbool(self.data_list, key, val, "lte")
            return dbool

        return common_lte

    def _common_op(self, key:str, op:str) -> Callable:
        def common_op(_self, val):
            dbool = self._dbool(self.data_list, key, val, op)
            return dbool

        return common_op

    # Private Subclasses
    class _dbool:
        """
        This class is responisble for logically fetching the data based on the fields or the stub heads (basically the keys of dicts)
        """

        def __init__(self, data_list:list, key:str, val:str, op_type:str="eq") -> None:
            self.data_list = data_list
            self.tuple = self._gen_tup(key, val, op_type)

        # Dundder methods
        def __repr__(self) -> str:
            """
            Prints the _dbool object using the prettytable module
            """

            x = prettytable.PrettyTable()
            x.field_names = ["index", "bool"]
            for i, z in enumerate(self.tuple):
                x.add_row([i, z])

            return f"{x}\n_dtype : DataFrame_dbool"

        def __and__(self, comp_obj:object) -> object:
            """
            Overloads the & to give a logical and for _dbool data
            """
            final_obj = self._compare(comp_obj, "and")
            return final_obj

        def __or__(self, comp_obj:object) -> object:
            """
            Overloads the | to give a logical or for _dbool data
            """
            final_obj = self._compare(comp_obj, "or")
            return final_obj

        # Private methods
        def _gen_tup(self, key:str, val:str, op_type:str) -> tuple:
            """
            Converts the data_list to tuple which is used for further comparision
            """
            final_tup = []
            for _, elem in enumerate(self.data_list):
                if op_type == "gt":
                    final_tup.append(elem[key] > val)
                elif op_type == "gte":
                    final_tup.append(elem[key] >= val)
                elif op_type == "lt":
                    final_tup.append(elem[key] < val)
                elif op_type == "lte":
                    final_tup.append(elem[key] <= val)
                elif op_type == "eq":
                    final_tup.append(elem[key] == val)
                elif op_type == "incl":
                    final_tup.append(val in str(elem[key]))
                elif op_type == "strw":
                    final_tup.append(str(elem[key]).startswith(val))
                elif op_type == "endw":
                    final_tup.append(str(elem[key]).endswith(val))
                else:
                    raise Exception("Invalid operation type!")

            return tuple(final_tup)

        def _compare(self, dbool_obj:object, op_type:str) -> tuple:
            """
            Used to compare the _dbool objects logically
            """
            tup = zip(self.tuple, dbool_obj.tuple)
            final_tup = []
            for x, y in tup:
                if op_type == "and":
                    final_tup.append(x == True and y == True)
                elif op_type == "or":
                    final_tup.append(x == True or y == True)
                else:
                    raise Exception("Invalid operation type !")

            self.tuple = tuple(final_tup)
            return self
# To be implemeted
# def read_csv(): 
#     pass

# def read_json(): 
#     pass

# def read_html(): 
#     pass


if __name__ == "__main__":
    # I am awesome like a pandas dataframe ^_^

    data = DataFrame(
        [
            {
                "id": 1,
                "data": "Hello wolrdEnim sunt ex cupidatat occaecat eiusmod aute ut officia. Esse esse aliqua aute excepteur ipsum reprehenderit veniam duis magna mollit. Nulla proident nostrud non non anim qui in. Ad anim nisi et dolore dolor minim duis adipisicing nostrud est cupidatat id. Velit ex dolore adipisicing duis labore officia deserunt reprehenderit tempor et dolor. Eiusmod aliqua commodo est et laboris labore mollit.",
                "uuid": "ghjk3878j321134",
                "color": "red",
            },
            {
                "id": 2,
                "data": "Ex aute adipisicing esse do excepteur dolore. Sunt deserunt sint tempor ad magna anim eu esse enim incididunt exercitation ipsum. Excepteur aliqua elit veniam consectetur exercitation eiusmod amet do incididunt cillum aliquip. Eiusmod nulla incididunt quis ex. Adipisicing mollit Lorem sunt aliqua ex voluptate exercitation. Qui ut ex qui et magna ut ad cupidatat cupidatat esse laborum dolore enim. Aliquip eiusmod quis eu ullamco veniam.",
                "uuid": "eihr8rhre8013nqfwe-9u",
                "color": "blue",
            },
            {
                "id": 3,
                "data": "Elit consectetur nisi esse fugiat anim irure. Id et non eu ullamco duis Lorem elit dolor sunt do id veniam. Sit id anim reprehenderit sint irure consectetur anim. Velit deserunt reprehenderit ea officia dolore aliquip sit incididunt culpa. Nostrud magna ut laboris nulla sit enim sunt deserunt eiusmod laboris adipisicing ea excepteur.",
                "uuid": "b08349m320m=-081",
            },
        ]
    )

    print("Printing the whole data table : ")
    print(data)
    print("\n")

    print("Printing the only id : ")
    print(data.id)
    print("\n")

    print("Printing the or condtion based table : ")
    print(data[(data.id == 3) | (data.color == "blue")])
    print("\n")

    print("Printing the and condtion based table : ")
    print(data[(data.id == 3) & (data.uuid == "b08349m320m=-081")])
    print("\n")
