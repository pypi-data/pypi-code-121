from collections import OrderedDict

from xml_utils.xsd_tree.xsd_tree import XSDTree

# from lxml import etree
# TODO :refactor etree function in xml_utils


OWL_NAMESPACE = "{http://www.w3.org/2002/07/owl#}"
RDFS_NAMESPACE = "{http://www.w3.org/2000/01/rdf-schema#}"
RDF_NAMESPACE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

CQL_NAMESPACE = "{http://siam.nist.gov/Database-Navigation-Ontology#cql:}"  # FIXME replace hard coded elements


def parse_ontology(ontology):
    """Create Navigation associated to the ontology

    Args:
        String/unicode object

    Returns: OrderedDict

    """

    owl_tree = XSDTree.fromstring(ontology)
    nav_tree = generate_classes(owl_tree)
    return nav_tree


def generate_classes(owl_tree):
    """Parse OWL Classes
    Args:
        owl_tree: Element tree

    Returns: OrderedDict

    """

    classes = OrderedDict()

    # TODO: replace by XSDTree.findall(owl_tree,"{}Class".format(OWL_NAMESPACE))
    owl_classes = owl_tree.findall("{}Class".format(OWL_NAMESPACE))
    # get the annotations of the ontology
    annotations = []
    # TODO: replace by XSDTree.findall(owl_tree, "{}AnnotationProperty".format(OWL_NAMESPACE))
    owl_annotations = owl_tree.findall("{}AnnotationProperty".format(OWL_NAMESPACE))

    for owl_annotation in owl_annotations:
        annotation = owl_annotation.attrib["{}about".format(RDF_NAMESPACE)]
        try:
            annotation_name = annotation.split(":")[-1]
        except Exception as exc:
            annotation_name = annotation

        annotations.append(annotation_name)

    for owl_class in owl_classes:
        # TODO: XSDTree.findall(owl_class, "{}subClassOf".format(RDFS_NAMESPACE))
        owl_subclasses = owl_class.findall("{}subClassOf".format(RDFS_NAMESPACE))

        # Top level if not subclass of other class
        if len(owl_subclasses) == 0:
            owl_class_name = owl_class.attrib["{}about".format(RDF_NAMESPACE)]

            classes[owl_class_name] = {
                "annotations": get_class_annotations(owl_class, annotations),
                "children": generate_subclasses(owl_tree, owl_class_name, annotations),
            }

    return classes


def generate_subclasses(owl_tree, base_class_name, annotations):
    """Parse OWL Subclasses
    Args:
        owl_tree: Element tree
        base_class_name:  String
        annotations: List

    Returns: OrderedDict
    """
    subclasses = OrderedDict()
    # TODO: use XSDTree
    owl_classes = owl_tree.findall("{}Class".format(OWL_NAMESPACE))
    # owl_classes = XSDTree.findall(owl_tree, "{}Class".format(OWL_NAMESPACE))
    for owl_class in owl_classes:
        # TODO: use XSDTree
        owl_subclasses = owl_class.findall("{}subClassOf".format(RDFS_NAMESPACE))
        # owl_subclasses = XSDTree.findall(owl_class, "{}subClassOf".format(RDFS_NAMESPACE))
        # Test if subclass of other class
        if len(owl_subclasses) > 0:
            for owl_subclass in owl_subclasses:
                resource_name = owl_subclass.attrib["{}resource".format(RDF_NAMESPACE)]

                if resource_name == base_class_name:
                    class_name = owl_class.attrib["{}about".format(RDF_NAMESPACE)]

                    subclasses[class_name] = {
                        "annotations": get_class_annotations(owl_class, annotations),
                        "children": generate_subclasses(
                            owl_tree, class_name, annotations
                        ),
                    }

                    break

    return subclasses


def get_class_annotations(owl_class, annotations):
    """Return annotations found in the class

    Args:
        owl_class: owl class to look in (Element tree)
        annotations: list of annotations to look for (list)

    Returns: Dict
    """
    # Get annotations of the class
    class_annotations = {}

    for annotation in annotations:
        # TODO: use XSDTree
        class_annotation = owl_class.find("{0}{1}".format(CQL_NAMESPACE, annotation))
        # class_annotation = XSDTree.iterfind(owl_class, "{0}{1}".format(CQL_NAMESPACE, annotation))
        if class_annotation is not None:
            class_annotations[annotation] = class_annotation.text

    return class_annotations
