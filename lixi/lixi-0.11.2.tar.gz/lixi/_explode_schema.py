import os, sys, re, io, copy
from lxml import etree

'''
e.g.

Create_Uncomplextypes_Schema.py "../../Schemas/LIXI-CAL-2_4_2-Annotated.xsd" "./Untyped_Schemas/LIXI-CAL-2_4_2-Annotated.xsd"

'''

ns = {'xs': 'http://www.w3.org/2001/XMLSchema',
      'lx': 'lixi.org.au/schema/appinfo_elements',
      'li': 'lixi.org.au/schema/appinfo_instructions'}
    
def load(path):
    '''
    Read Schema from file
    '''
    #with open(path) as file:
        #data = file.read().
        #return etree.fromstring(data)
        
    
    f = io.open(path, mode="r", encoding="utf-8")
    data =  f.read()
    
    data = bytes(bytearray(data, encoding='utf-8'))
    
    parser = etree.XMLParser(remove_blank_text=True)

    
    return etree.fromstring(data, parser)
    
    
def save(outputpath, filename, schema):
    '''
    Write Schema to file
    '''
    schema_string = etree.tostring(schema, pretty_print=True, encoding='UTF-8')
   
    
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)    
    
    with open(outputpath + filename, 'wb+') as file:
        file.write(schema_string)
        
        
def clone(item):
    return copy.deepcopy(item)

def get_all_lixi_elements (schema):
    xpath = "//xs:element"
    return schema.xpath(xpath, namespaces=ns)

def get_all_lixi_items (schema):
    xpath = ".//xs:element|.//xs:attribute"
    return schema.xpath(xpath, namespaces=ns)

def get_all_lixi_paths (schema):
    xpath = "//lx:path"
    return schema.xpath(xpath, namespaces=ns)

def get_all_lixi_complex_types (schema):
    xpath = "/xs:schema/xs:complexType"
    return schema.xpath(xpath, namespaces=ns)

def get_all_lixi_elements_using_a_complex_type (schema, complextype):
    name = names([complextype])[0]
    xpath = "//xs:element[@type='"+ name +"']"
    return schema.xpath(xpath, namespaces=ns)

def get_package_element (schema):
    xpath = "/xs:schema/xs:element[@name='Package']"
    return schema.xpath(xpath, namespaces=ns)[0]

def get_item (schema, path):
    ''' given a path, get the schema item '''
    xpath = "//lx:path[text()='"+path+"']/../../.."
    return schema.xpath(xpath, namespaces=ns)[0]

def get_decendants (node):
    ''' given an lxml schema node, return a list of lixi items (elements, attributes, enumerations) that are decendants'''
    return node.xpath('.//xs:element|.//xs:attribute|.//xs:enumeration', namespaces=ns)
    
    



def intersection(one, two):
    '''
    given two list of elements, return the items found in both lists
    '''
    a = set(one)
    b = set(two)
    return a.intersection(b)    


def urls(items):
    '''
    given a list of schema item, return a list of the relative URL of the item in the documentation
    '''
    urls = []

    for item in items:
        tag = tags([item])[0]
        path = paths([item])[0]
        name = names([item])[0]

        url = '../' + tag + '/index.html#' + path


        if tag == 'enumeration':
            x = len('.' + name) 
            path = path[:-x]
            url = '../simpletype/index.html#' + path + '-simpletype'

        else:
            url = '../' + tag +  '/index.html#' + path    

        urls.append(url)

    return urls


def subschema(schema, transaction):
    '''
    Given a schema and a transaction type (e.g. 'DAS'), return all schema items in the subschema.
    '''
    return schema.xpath('//li:transactions[contains(.,"' + transaction + '")]/../../..', namespaces=ns)


def subschema_exclusive(schema, transaction):
    '''
    Given a schema and a transaction type (e.g. 'DAS'), return all schema items in only found in this subschema.
    '''
    return schema.xpath("//li:transactions[text()='"+transaction+"']/../../..", namespaces=ns)


def deprecated(schema):
    '''
    return the items that are being deprecated
    '''
    return schema.xpath('//xs:documentation[contains(.,"deprecated")]/../..', namespaces=ns)
    
 
def references(schema):
    '''
    return the items that are cross references
    '''
    return schema.xpath('//xs:attribute[contains(.,"x_")]', namespaces=ns)

def get_name (item):
    if item.tag == '{http://www.w3.org/2001/XMLSchema}enumeration':
        return item.attrib['value']
    else: 
        return item.attrib['name']

def names(items):
    '''
    given a list of lxml schema items, return a list of names (or values for enumerations)
    '''
    result = []
    for item in items:
        if item.tag == '{http://www.w3.org/2001/XMLSchema}enumeration':
            result.append(item.attrib['value'])
        else: 
            result.append(item.attrib['name'])
    return result

def get_path (item):
    
    return item.getchildren()[0].getchildren()[1].getchildren()[0].text

def paths(items):
    '''
    Given a list of lxml schema items, return a list of paths
    '''
    result = []
    for item in items:
        result.append(item.getchildren()[0].getchildren()[1].getchildren()[0].text)
    return result


def labels(items):
    '''
    Given a list of lxml schema items, return a list of labels
    '''
    result = []
    for item in items:
        result.append(item.getchildren()[0].getchildren()[1].getchildren()[1].text)
    return result


def transactions(items):
    '''
    Given a list of lxml schema items, return a list of transaction tags
    '''
    result = []
    for item in items:
        result.append(item.getchildren()[0].getchildren()[1].getchildren()[2].text)
    return result


def items (schema, paths):
    '''
    Given a list of paths, return a list of lxml objects 
    '''
    result=[]
    for path in paths:
        path = path.replace("'","&apos;")
        items = schema.xpath("//lx:path[text()='"+path+"']/../../..", namespaces=ns)
        if len(items) > 0:
            result.append(items[0])
    return result


def types(items):
    '''
    Given a list of lxml schema items, return a list of types
    '''
    result = []
    for item in items:
        if 'type' in item.attrib:
            result.append(item.attrib['type'])
        else:
            result.append("")
    return result


def uses(items):
    '''
    Given a list of lxml schema items, return a list of uses
    '''
    result = []
    for item in items:
        if 'use' in item.attrib:
            result.append(item.attrib['use'])
        else:
            result.append("")
    return result


def item_types(items):
    '''
    Given a list of lxml schema items, return a list of xml types ("element", "attribute", "enumeration, "simpleType", or "complextType")
    '''
    result = []
    for item in items:
        tag = item.tag.replace("{http://www.w3.org/2001/XMLSchema}",'')
        result.append(tag)
    return result


def documentations(items):
    '''
    given a list of lxml schema items, return a list of paths
    '''
    result = []
    for item in items:
        result.append(item.getchildren()[0].getchildren()[0].text)
    return result


def minOccurs (items):
    '''
    given a list of lxml schema items, return a list of minOccurs
    '''
    result = []
    for item in items:
        if 'minOccurs' in item.attrib:
            result.append(item.attrib['minOccurs'])
        else:
            result.append("1")
    return result

def maxOccurs (items):
    '''
    given a list of lxml schema items, return a list of maxOccurs
    '''
    result = []
    for item in items:
        if 'maxOccurs' in item.attrib:
            result.append(item.attrib['maxOccurs'])
        else:
            result.append("")
    return result


def gettype(schema, name):
    '''
    Given a schema and a type name, return the complex type element, or simple type elememnt 
    '''
    return schema.xpath('//xs:complexType[@name="' + name + '"]', namespaces=ns)[0]


def getchildren(item):
    '''
    Given an lxml lixi element, return the lixi child elements as lxml objects
    '''
    children = []
    
    if item.tag == '{http://www.w3.org/2001/XMLSchema}complexType':
        child_elements = item.getchildren()[1].getchildren()[1:]
        for child_element in child_elements:
            children.append(child_element)
        
    else:    
    
        item.getchildren()
        if len(item.getchildren()) > 1:
            child_elements = item.getchildren()[1][0].getchildren()
            for child_element in child_elements:
                if (child_element.tag == '{http://www.w3.org/2001/XMLSchema}element'):
                    children.append(child_element)
                
    return children


def getchildren_include_choices(item):
    '''
    Given an lxml lixi element, return the lixi child elements as lxml objects
    '''
    children = []

    child_elements = item.xpath('./xs:complexType/xs:choice/xs:sequence/xs:choice/xs:element|./xs:complexType/xs:choice/xs:sequence/xs:choice/xs:sequence/xs:element|./xs:complexType/xs:choice/xs:sequence/xs:element|./xs:complexType/xs:sequence/xs:sequence/xs:element|./xs:complexType/xs:sequence/xs:element|./xs:complexType/xs:sequence/xs:choice/xs:element|./xs:complexType/xs:choice/xs:element|./xs:complexType/xs:sequence/xs:choice/xs:sequence/xs:element', namespaces=ns)
    

    
    for child_element in child_elements:
        if (child_element.tag == '{http://www.w3.org/2001/XMLSchema}element'):
            children.append(child_element)
            
            
    return children


def getattributes(item):
    '''
    Given an lxml lixi element, return its lixi attributes as lxml objects
    '''    
    attributes = []
    if item.tag == '{http://www.w3.org/2001/XMLSchema}complexType':
        child_elements = item.getchildren()[1:]
        for child_element in child_elements:
            if child_element.tag == '{http://www.w3.org/2001/XMLSchema}attribute':
                attributes.append(child_element)   
                
    return attributes


def annotation (schema, documentation, path, label, transactions):
    
    # create new annotation
    new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
    new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')    
    new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
    new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
    new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
    new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')
    
    # build tree
    new_annotation.append (new_documentation)
    new_annotation.append (new_appinfo)
    new_appinfo.append    (new_path)
    new_appinfo.append    (new_label)
    new_appinfo.append    (new_transactions)
    
    # set values
    new_documentation.text = documentation
    new_path.text          = path
    new_label.text         = label
    new_transactions.text  = transactions    
    
    # get the old element
    parent_xpath = '//lx:path[text()="'+path+'"]'
    path_element = schema.xpath(parent_xpath, namespaces=ns)[0]
    element      = path_element.getparent().getparent().getparent()
    
    # swap the annotation
    old_annotation = element.getchildren()[0]
    element.remove(old_annotation)
    element.insert(0, new_annotation)
    
    return element

    
    
def element(schema, name, minOccurs, maxOccurs, type_, documentation, path, label, transactions):
        
    # check if the element exists
    xpath   = '//lx:path[text()="' + path + '"]'
    matches = schema.xpath(xpath, namespaces=ns)
    
    if len(matches) == 0:
        
        print("    element does not exist: " + path) 
        
        # create the new element
        new_element = etree.Element('{http://www.w3.org/2001/XMLSchema}element')
        new_element.set('name', name)
        if type_ != '':
            new_element.set('type', type_)            
        new_element.set('minOccurs', minOccurs)
        new_element.set('maxOccurs', maxOccurs)

        # create child elements 
        new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
        new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
        new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
        new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
        new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
        new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')
        new_complextype   = etree.Element('{http://www.w3.org/2001/XMLSchema}complexType')
        new_sequence      = etree.Element('{http://www.w3.org/2001/XMLSchema}sequence')
         
        # build tree
        new_element.append     (new_annotation)
        new_annotation.append  (new_documentation)
        new_annotation.append  (new_appinfo)
        new_appinfo.append     (new_path)
        new_appinfo.append     (new_label)
        new_appinfo.append     (new_transactions)
        new_element.append     (new_complextype)
        new_complextype.append (new_sequence)
        
        # set values
        new_documentation.text = documentation
        new_path.text          = path
        new_label.text         = label
        new_transactions.text  = transactions
        
        # get parent element
        parent_path = re.sub(r'.%s$' % name, '', path)
        parent_xpath = '//lx:path[text()="'+parent_path+'"]'
        parent_path_element = schema.xpath(parent_xpath, namespaces=ns)[0]
        parent_element = parent_path_element.getparent().getparent().getparent()
        complextype_element = parent_element.getchildren()[1]
        if (complextype_element.tag == '{http://www.w3.org/2001/XMLSchema}sequence'):
            sequence_element    = complextype_element
        else:
            if (len(complextype_element.getchildren()) == 0):
                sequence_element = etree.Element('{http://www.w3.org/2001/XMLSchema}sequence')
                complextype_element.append(sequence_element)
            else:
                sequence_element    = complextype_element.getchildren()[0]    
            if   (sequence_element.tag == '{http://www.w3.org/2001/XMLSchema}choice'):
                pass
            elif (sequence_element.tag != '{http://www.w3.org/2001/XMLSchema}sequence'):
                complextype_element.insert(0, etree.Element('{http://www.w3.org/2001/XMLSchema}sequence'))
                sequence_element    = complextype_element.getchildren()[0]   
                
        # insert in correct place
        siblings = sequence_element.getchildren()
        if len(siblings) == 0:
            sequence_element.append(new_element)
        else:
            found = False
            for sibling in siblings:
                if sibling.attrib['name'].lower() > new_element.attrib['name'].lower():                
                    sequence_element.insert((sequence_element.index(sibling)), new_element)
                    found = True
                    break
            if not found:
                sequence_element.append(new_element)
                
        removesequences(schema)

        result = new_element
        
    # if we are updating an existing element
    else:
        
        print("    element does exist: " + path) 
        
        old_element = matches[0].getparent().getparent().getparent()
        if path != 'Package':     
            old_element.attrib['minOccurs'] = minOccurs
            old_element.attrib['maxOccurs'] = maxOccurs

        # delete annotation
        old_element.remove(old_element.getchildren()[0])
    
        # create new annotation
        new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
        new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
        new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
        new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
        new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
        new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')
    
        # build tree
        old_element.insert     (0, new_annotation)
        new_annotation.append  (new_documentation)
        new_annotation.append  (new_appinfo)
        new_appinfo.append     (new_path)
        new_appinfo.append     (new_label)
        new_appinfo.append     (new_transactions)
    
        # set values
        new_documentation.text = documentation
        new_path.text          = path
        new_label.text         = label
        new_transactions.text  = transactions        
    
        result = old_element                

    return result
  

def enumeration(schema, name, documentation, path, label, transactions):
    
    # get parent element
    path_with_dot = path.replace("[-]",".") # some enumeration paths have had a "." replace with "[-]" e.g. "insurerList.Smart Business Insurance Pty Ltd[-]"
    parent_path = path_with_dot.replace('.'+name, '')
    parent_xpath = '//lx:path[text()="'+parent_path+'"]'
    parent_path_element = schema.xpath(parent_xpath, namespaces=ns)[0]
    parent_element = parent_path_element.getparent().getparent().getparent()  
    restriction_element = parent_element.getchildren()[1]  
    
    # get enumerations of this list
    siblings = restriction_element.getchildren()

    # check if the enumeration already exists (on the basis of its name)
    simple_type_already_exists = name in names(siblings)    
    
    if simple_type_already_exists:
        # get old element and remove its annotation
        xpath = '//lx:path[text()="'+path+'"]/../../..'
        old_element = schema.xpath(xpath, namespaces=ns)[0]
        old_element.remove(old_element.getchildren()[0])
        new_element = old_element        
    else:
        # create new element
        new_element = etree.Element('{http://www.w3.org/2001/XMLSchema}enumeration')
        new_element.set('value', name)

    # create sub-elements 
    new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
    new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
    new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
    new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
    new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
    new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')

    # build tree
    new_element.append     (new_annotation)
    new_annotation.append  (new_documentation)
    new_annotation.append  (new_appinfo)
    new_appinfo.append     (new_path)
    new_appinfo.append     (new_label)
    new_appinfo.append     (new_transactions)

    # set values
    new_documentation.text = documentation
    new_path.text          = path
    new_label.text         = label
    new_transactions.text  = transactions
    
    # insert in correct place
    
    if len(siblings) == 0:
        restriction_element.append(new_element)
    else:
        found = False
        for sibling in siblings:
            if sibling.attrib['value'].lower() > new_element.attrib['value'].lower():                
                restriction_element.insert((restriction_element.index(sibling)), new_element)
                found = True
                break
        if not found:
            restriction_element.append(new_element)   
            
    return new_element

        
def attribute(schema, name, type_, use, documentation, path, label, transactions):
    
    # check if the element exists
    xpath   = '//lx:path[text()="' + path + '"]'
    matches = schema.xpath(xpath, namespaces=ns)
    
    if len(matches) == 0:
        
        print("    attribute does not exist: " + path)
        
        # get parent element
        parent_path = re.sub(r'.%s$' % name, '', path)
        parent_xpath = '//lx:path[text()="'+parent_path+'"]'
        parent_path_element = schema.xpath(parent_xpath, namespaces=ns)[0]
        parent_element = parent_path_element.getparent().getparent().getparent()  

        # ###################################
        # Create a new attribute
        # ###################################
               
        new_element = etree.Element('{http://www.w3.org/2001/XMLSchema}attribute')
        new_element.set('name', name)
        new_element.set('type', type_)
        new_element.set('use', use)
        
        # create elements 
        new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
        new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
        new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
        new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
        new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
        new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')
         
        # build tree
        new_element.append     (new_annotation)
        new_annotation.append  (new_documentation)
        new_annotation.append  (new_appinfo)
        new_appinfo.append     (new_path)
        new_appinfo.append     (new_label)
        new_appinfo.append     (new_transactions)
                
        # set values
        new_documentation.text = documentation
        new_path.text          = path
        new_label.text         = label
        new_transactions.text  = transactions
        
        # ##############################
        # get the element to which the attributes will be appended 
        # ##############################
        
        # #########################
        # if it is a complex type (i.e. SignatureType) 
        # the attributes are appended to the "xs:complexType" element 
        # as a sibling to, and after, the annotation and the sequence
        # #########################
        if str(parent_element.tag) == "{http://www.w3.org/2001/XMLSchema}complexType":
            append_to = parent_element   # this is the element to append the attributes to
            siblings  = append_to.getchildren()[2:]    # the annotation and the sequence we only care about the attributes
            indent    = 2   # remember to append after the annotation and the sequence
            
        # #########################
        # if it is a normal element
        # the attributes are appended to the "xs:complexType" element 
        # which is a child of the element element
        # after the sequence element (if there is one)
        # #########################       
        elif str(parent_element.tag) == "{http://www.w3.org/2001/XMLSchema}element":
            children = parent_element.getchildren() # children should be "annotation" and "complexType"
            if children[1].tag == "{http://www.w3.org/2001/XMLSchema}complexType": # check that is is a complex type element where expected
                append_to = children[1]
                siblings  = append_to.getchildren()
                if len(append_to) > 0 and append_to[0].tag == "{http://www.w3.org/2001/XMLSchema}sequence": # if the LIXI element has LIXI child elements
                    siblings = siblings[1:]  # ignore the first one (the sequence) we don't care about LIXI elements only the attributes
                    indent = 1  # remember to insert after the sequence (index 1)
                else:
                    indent = 0  # don't worry about inserting  after the sequence
            else:
                
                raise Exception ("Expected 'complextType' got: " + str(children[1].tag))
        else:
            raise Exception("Expected type of: 'complexType' or 'element' instead got: " + str(parent_element.tag))
 
        
        # #####################################
        # if there are no attributes here, go ahead and add the new one
        # #####################################
        if len(siblings) == 0:
            append_to.insert(indent, new_element)
        
        else: 
            # get the name of the new attribute
            new_element_name = new_element.attrib['name'].lower()
            
            # if the first attribute is higher alphabetically, add the new one to the start
            if siblings[0].attrib['name'].lower() > new_element_name:   
                append_to.insert(indent, new_element)
                
            # get the position of the new attribute
            else:  
                found = False
                for sibling in siblings:
                    if  sibling.attrib['name'].lower() > new_element_name:     
                        position = append_to.index(sibling) 
                        append_to.insert((position), new_element)
                        found = True
                        break
                    
                # otherwise put it on the end
                if not found:
                    append_to.append(new_element)   
                    
        result = new_element
    
    # ###########################################                
    # if we are updating an existing element
    # ###########################################
    else:
        
        print("    attribute does exist")
        
        old_element = matches[0].getparent().getparent().getparent()
        old_element.attrib['type'] = type_
        old_element.attrib['use']  = use
        
        # delete annotation
        old_element.remove(old_element.getchildren()[0])
        
        # create new annotation
        new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
        new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
        new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
        new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
        new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
        new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')
    
        # build tree
        old_element.append     (new_annotation)
        new_annotation.append  (new_documentation)
        new_annotation.append  (new_appinfo)
        new_appinfo.append     (new_path)
        new_appinfo.append     (new_label)
        new_appinfo.append     (new_transactions)
    
        # set values
        new_documentation.text = documentation
        new_path.text          = path
        new_label.text         = label
        new_transactions.text  = transactions        
    
        result = old_element        
                
    return result
            
        
            
def simpletype (schema, name, documentation, path, label, transactions):
    
    # get all the simple types
    simpleTypesAll = schema.xpath("./xs:simpleType", namespaces=ns)
    
    # check if the simple type already exists (on the basis of its name)
    simple_type_already_exists = name in names(simpleTypesAll)
    
    if simple_type_already_exists:
        old_element = schema.xpath("./xs:simpleType[@name='" + name + "']", namespaces=ns)[0]
        # remove the old annotations
        old_element.remove(old_element.getchildren()[0])
        new_element = old_element
        
    else:
        # create new simple type element
        new_element = etree.Element('{http://www.w3.org/2001/XMLSchema}simpleType')
        new_element.set('name', name)        

    # create child elements 
    new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
    new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
    new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
    new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
    new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
    new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')
   
    # build the tree
    new_element.insert (0, new_annotation)
    new_annotation.append  (new_documentation)
    new_annotation.append  (new_appinfo)
    new_appinfo.append     (new_path)
    new_appinfo.append     (new_label)
    new_appinfo.append     (new_transactions)
    
    # set values
    new_documentation.text = documentation
    new_path.text          = path
    new_label.text         = label
    new_transactions.text  = transactions
    
    # if the simple type is new, append a restriction element
    if not simple_type_already_exists:
        new_restriction   = etree.Element('{http://www.w3.org/2001/XMLSchema}restriction')
        new_element.append     (new_restriction)
        new_restriction.set('base','xs:token')
    
    # sort the simple type into the three categories: 'list' 'pattern' and 'type' 
    simpleTypesLists = []
    simpleTypesPatterns = []
    simpleTypesTypes = []     
    
    # add the other elements to the correct lists
    for simpleType in simpleTypesAll:
        name_ = simpleType.attrib['name'].lower()
        if name_.endswith('list'):
            simpleTypesLists.append(simpleType)  
        elif name_.endswith('pattern'):
            simpleTypesPatterns.append(simpleType) 
        elif name_.endswith('type'):
            simpleTypesTypes.append(simpleType)
            
    # get position of new item
    position = len(schema.xpath("./xs:complexType", namespaces=ns)) + 2
    
    if name.endswith('List'):
        for sibling in simpleTypesLists:
            if sibling.attrib['name'].lower() > new_element.attrib['name'].lower():                
                break
            position += 1
            
    if name.endswith('Pattern'):
        position += len(simpleTypesLists)
        for sibling in simpleTypesPatterns:
            if sibling.attrib['name'].lower() > new_element.attrib['name'].lower():                
                break
            position += 1        
            
    if name.endswith('Type'):
        position += len(simpleTypesLists) + len(simpleTypesPatterns)
        for sibling in simpleTypesTypes:
            if sibling.attrib['name'].lower() > new_element.attrib['name'].lower():                
                break
            position += 1          
        
    schema.insert(position, new_element)    
    
    return new_element


def put_complextype (schema, name, documentation, path, label, transactions):
    


    # get all the complex types
    complexTypesAll = schema.xpath("./xs:complexType", namespaces=ns)

    # if the complex type already exists
    if name in names(complexTypesAll):
        
        # get the old complex type element
        old_element = schema.xpath("./xs:complexType[@name='" + name + "']", namespaces=ns)[0]
        
        # delete the old annotation
        old_element.remove(old_element.getchildren()[0]) 
        
        # create child elements 
        new_annotation    = etree.Element('{http://www.w3.org/2001/XMLSchema}annotation')
        new_documentation = etree.Element('{http://www.w3.org/2001/XMLSchema}documentation')
        new_appinfo       = etree.Element('{http://www.w3.org/2001/XMLSchema}appinfo')
        new_path          = etree.Element('{lixi.org.au/schema/appinfo_elements}path')
        new_label         = etree.Element('{lixi.org.au/schema/appinfo_elements}label')
        new_transactions  = etree.Element('{lixi.org.au/schema/appinfo_instructions}transactions')        
        
        # build tree
        old_element.insert     (0, new_annotation)
        new_annotation.append  (new_documentation)
        new_annotation.append  (new_appinfo)
        new_appinfo.append     (new_path)
        new_appinfo.append     (new_label)
        new_appinfo.append     (new_transactions)
        
        # set values
        new_documentation.text = documentation
        new_path.text          = path
        new_label.text         = label
        new_transactions.text  = transactions        
        
        new_element = old_element
        
    else:
        
        # create new complex type element
        new_element = etree.Element('{http://www.w3.org/2001/XMLSchema}complexType')
        new_element.set('name', name)
        
        raise Exception ("The function to add a new complex type has not been finalised.")
        
    return new_element
 
    
        
  
def removesequences(schema):      
    # remove empty sequences
    empty_sequences = schema.xpath('//xs:sequence[not(*)]', namespaces=ns)
    for empty in empty_sequences:
        empty.getparent().remove(empty)


def removecomplextypes(schema):         
    # remove empty complextype
    empty_complexType = schema.xpath('//xs:complexType[not(*)]', namespaces=ns)
    for empty in empty_complexType:
        empty.getparent().remove(empty)    


def main(annotated_unexploded_schema):

    
    schema       = annotated_unexploded_schema
    elements     = get_all_lixi_elements(schema)
    complexTypes = get_all_lixi_complex_types(schema)
    
    
    
    rootelement  = 'Package'
    annotations  = True
    update_paths = True
    
    for complextype in complexTypes:
        complextype_name = get_name(complextype)
        elements_using_the_type = get_all_lixi_elements_using_a_complex_type(schema, complextype)
        
        for element_using_the_type in elements_using_the_type:
            
            
            
            minoccurs_of_element_using_the_type = minOccurs([element_using_the_type])[0]
            maxoccurs_of_element_using_the_type = maxOccurs([element_using_the_type])[0]
            
            if maxoccurs_of_element_using_the_type == "": 
                maxoccurs_of_element_using_the_type = "1"
    
            cloned_complextype             = clone(complextype)
            cloned_complextype_paths       = get_all_lixi_paths(cloned_complextype)
            
            
            if update_paths:
                name_of_element_using_the_type = get_name(element_using_the_type)
                path_of_element_using_the_type = get_path(element_using_the_type)        
        
                for path in cloned_complextype_paths:
                    path.text = path.text.replace(complextype_name, path_of_element_using_the_type) 
                
            if annotations:
                cloned_complextype_children = cloned_complextype.getchildren()[1:]
                
            else: 
                cloned_complextype_children = cloned_complextype.getchildren()
            
            # add a '<xs:complexType' element under the element using the complex type
            
            new_complextype_element = etree.Element('{http://www.w3.org/2001/XMLSchema}complexType')
            
    
            element_using_the_type.append(new_complextype_element)
            
            for child in cloned_complextype_children:
                new_complextype_element.append(child)
                
            # remove the 'type' attribute from the element using the complex type
            element_using_the_type.attrib.pop('type')
            
            element_using_the_type.attrib['minOccurs'] = minoccurs_of_element_using_the_type
            
            element_using_the_type.attrib['maxOccurs'] = maxoccurs_of_element_using_the_type
            
        complextype.getparent().remove(complextype) 
        
    root_elements = schema.getchildren()
        
    for child in root_elements:
        
        if 'name' in child.attrib and not child.attrib['name'] == rootelement and not child.tag == "{http://www.w3.org/2001/XMLSchema}simpleType" :
    
            child.getparent().remove(child)
                
    annotated_exploded_schema = schema
                
    return annotated_exploded_schema  