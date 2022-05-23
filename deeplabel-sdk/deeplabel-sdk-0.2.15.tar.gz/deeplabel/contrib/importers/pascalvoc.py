import os
from time import sleep
from typing import Callable, Dict, List, Set, Tuple, TypeVar, Optional
import xml.etree.ElementTree as ET
import dataclasses
from glob import glob
import logging
import tempfile
from tqdm.contrib.concurrent import process_map
from functools import partial

from deeplabel.label.label_maps import LabelMap
from deeplabel.projects import Project
from deeplabel.types.bounding_box import BoundingBox
from deeplabel.label.gallery.detections import Detection
from deeplabel.label.labels import DetectionLabel
from deeplabel.client import BaseClient
from deeplabel.label.gallery import Gallery
from deeplabel.label.gallery.images import Image, ImageDetectionType
from deeplabel.label.folders import Folder
from deeplabel.contrib.importers.utils import img_shape_from_url
from deeplabel.exceptions import handle_deeplabel_exceptions
import coloredlogs
coloredlogs.install('DEBUG')

logger = logging.getLogger(__name__)
missing_labels_file = os.path.join(tempfile.gettempdir(), "missing_label.txt")

@dataclasses.dataclass
class ImageDatasetImporter:
    annotation_root:str # folder that has all the xml files
    image_root:Optional[str] # folder that has all the jpg/png files
    url_provider:Optional[Callable[[str],str]] # function that takes filename and return it's url.
    folder_id:str # Folder to put the gallery-images into
    image_gallery_name:str # Name of the dataset
    client:BaseClient
    label_map:Dict[str,DetectionLabel] = dataclasses.field(default_factory=dict, init=False) # mapping labels to their label_id

    def __post_init__(self):
        assert (self.url_provider is not None), f"Currently, image upload is not supported in sdk, hence you must push the images to a cloud location manually and provide url_provider that would provide image url for each image"

    def run(self):
        logger.info(f"Checking if all labels exist")
        missing_labels = self.check_labels()
        if missing_labels:
            logger.error(f"Missing labels in Deeplabel {missing_labels}")
            with open(missing_labels_file,'w') as f:
                f.write("\n".join(missing_labels))
            logger.info(f"dumping missing labels to {missing_labels_file}")
            exit()
        
        folder = Folder.from_folder_id(self.folder_id, self.client)
        if gallery:=Gallery._from_search_params({
            "title":self.image_gallery_name,
            "projectId":folder.project_id,
            "parentFolderId":folder.folder_id},
            client=self.client):
            gallery=gallery[0]
            logger.info(f"Found existing gallery {gallery.title} {gallery.gallery_id}")
        else:
            logger.info(f"Creating new Gallery")
            gallery = Gallery.create(self.image_gallery_name, folder.project_id, folder.folder_id, self.client)
            logger.info(f"New Gallery created {gallery.title} {gallery.gallery_id}")
        logger.info(f"All labels exist in deeplabel... Starting import")
        xml_files = glob(os.path.join(self.annotation_root, '*.xml'))
        images = process_map(partial(self.upload_one_image, gallery_id=gallery.gallery_id), xml_files)
        assert len(images)==len(xml_files), f"There should be 1 image per xml file"
        gallery.submit_for_labelling()
        ready_to_label = False
        while not ready_to_label:
            logger.info(f"Waiting for gallery label task")
            tasks = gallery.tasks
            for task in tasks:
                if task.name=='LABEL':
                    task.change_status('IN_PROGRESS')
                    ready_to_label=True
                    break
            logger.debug(f"Sleeping for 5 sec while waiting for LABEL task to appear for gallery {gallery.title} {gallery.gallery_id}")
            sleep(5)
        process_map(self.insert_detections, list(zip(images, xml_files)))


    def upload_one_image(self, xml_file:str, gallery_id:str):
        filename, label_boxes = read_content(xml_file)
        url = self.url_provider(filename) #type: ignore
        w,h = img_shape_from_url(url)
        assert (h is not None) and (w is not None), "Couldn't find image shape from url"
        image = Image.create(url, gallery_id, h, w, filename, self.client)
        return image
    
    def insert_detections(self, image_and_path:Tuple[Image,str]):
        image, xml_file = image_and_path
        filename, label_boxes = read_content(xml_file)
        detections:List[Detection] = []
        h,w = image.resolution.height, image.resolution.width
        for label, bbox in label_boxes:
            det = Detection( #type: ignore
                detection_id=None,
                is_reviewed=False,
                bounding_box=BoundingBox(
                    xmin=max(0, bbox['xmin']/w),
                    xmax=min(1,bbox['xmax']/w),
                    ymin=max(0,bbox['ymin']/h),
                    ymax=min(1,bbox['ymax']/h)
                ),
                type=ImageDetectionType.bounding_box,
                client=None,
                label=self.label_map[label])
            detections.append(det)
        image.insert_detections(detections)


    def check_labels(self)->List[str]:
        """check if all the labels exist in deeplabel and return missing labels so they can be added manually"""
        annotations = glob(os.path.join(self.annotation_root, '*.xml'))
        missing_labels:Set[str] = set() # Labels that don't exist in deeplabel
        add_to_project:Set[str] = set() # labels taht exist but need adding to project
        labels = set()
        for ann_file in annotations:
            for obj in ET.parse(ann_file).getroot().iter('object'):
                labels.add(obj.find("name").text)
        folder = Folder.from_folder_id(self.folder_id, client=self.client)
        project = Project.from_project_id(folder.project_id, self.client)
        project_label_map = project.label_map

        for label in labels:
            found_existing = False
            for existing_label in DetectionLabel.from_search_params({'name':label}, self.client):
                if existing_label.name == label:
                    found_existing = True
                    self.label_map[label] = existing_label
                    break
            if not found_existing:
                missing_labels.add(label)
                continue
            found_in_project = False
            for label_map in project_label_map:
                if label_map.label_id == self.label_map[label].label_id:
                    logger.debug(f"Label {label} exists in the project")
                    found_in_project = True
                    break
            if not found_in_project:
                add_to_project.add(self.label_map[label].label_id)
        
        logger.info(f"Adding {len(add_to_project)} labels to project")
        if add_to_project:
            LabelMap.add_labels_to_project(project.project_id, list(add_to_project), self.client)
        return list(missing_labels)


filename = TypeVar('filename', bound=str)
label = TypeVar('label', bound=str)
    
def read_content(xml_file: str)->Tuple[filename, List[Tuple[str, Dict[str,int]]]]:
    """Read Pascalvoc annotation file, and return filename, and a list of label and bbox dict
    copied from https://stackoverflow.com/a/53832130
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()

    list_with_label_and_boxes = []
    filename = root.find('filename').text

    for box in root.iter('object'):
        label = box.find("name").text
        assert label is not None, f"couldn't find label key in file {xml_file}"
        bbox = {
            "ymin" : int(box.find("bndbox/ymin").text),
            "xmin" : int(box.find("bndbox/xmin").text),
            "ymax" : int(box.find("bndbox/ymax").text),
            "xmax" : int(box.find("bndbox/xmax").text)
        }

        list_with_label_and_boxes.append((label, bbox))

    return filename, list_with_label_and_boxes


def get_label(label:str, client:"BaseClient")->Optional[DetectionLabel]:
    for existing_label in DetectionLabel.from_search_params({'name':label}, client):
        if existing_label.name == label:
            return existing_label