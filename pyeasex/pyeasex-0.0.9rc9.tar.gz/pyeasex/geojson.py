import copy
import json

def merge(feature_collection, layer_label_prefix="Layer", algorithm="SAME_COORDINATES"):
  if algorithm == "SAME_COORDINATES":
    feature_dict = {}
    for feature in feature_collection["features"]:
      geometry_type = feature["geometry"]["type"]
      coordinates = feature["geometry"]["coordinates"]
      if geometry_type not in feature_dict:
        feature_dict[geometry_type] = {}

      coordinates_string = '#'.join(str(e) for e in coordinates)
      if coordinates_string not in feature_dict[geometry_type]:
        feature_dict[geometry_type][coordinates_string] = []      
      feature_dict[geometry_type][coordinates_string].append(feature)


    feature_collection["features"] = []
    for geometry_type in feature_dict:
      for coordinates_string in feature_dict[geometry_type]:
        features = feature_dict[geometry_type][coordinates_string]
        is_multi_layer = True if len(features) > 0 else False
        
        if is_multi_layer == True:
          align_feature = copy.deepcopy(features[0])
          align_feature["properties"] = {}
          for idx, feature  in enumerate(features):
            property_list = copy.deepcopy(list(feature["properties"].keys()))
           
            layer_label = "properties#{}-{}".format(layer_label_prefix, idx + 1)
            align_feature["properties"][layer_label] = {}
            for property in property_list:
              if idx == 0 and "ease-x#" in property:
                align_feature["properties"][property] = feature["properties"][property]
              elif "ease-x#" not in property:
                align_feature["properties"][layer_label][property] = feature["properties"][property]
                                  
          align_feature["properties"]["ease-x#multi-layer"] = True
 
        feature_collection["features"].append(align_feature)                  
      
  return json.dumps(feature_collection, ensure_ascii=False)
