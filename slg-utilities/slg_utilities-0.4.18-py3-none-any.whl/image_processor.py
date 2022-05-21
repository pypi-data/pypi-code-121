

from .helpers import *

import gridfs
import base64
import io


class ImageHandler:

    '''
    Standard format of images will be a bytestring, from there can format into useable
    stored objects, or decode them back into their base64 image

    Parameters
    ----------

    images: list
            list of image byte arrays (handling for other formats not supported, yet)

    image_filenames: list : optional
            list of image_filenames that can be zipped into 2 tuple format with
            defaults to f"image{idx+1}"


    DISCLAIMER:
            My understanding of image formats is limited and so
            initialization is currently limited to subclass 'ImgProcessorJS'
            ImageHandler.detect_format() will be used in the future to determine how to reduce
            a list of images to a list of image byte arrays
    '''

    def __init__(self, images=[], image_filenames=[]):
        self.images = images
        self.image_filenames = image_filenames

    def detect_format(self):
        '''
        want to detect current to know how to reformat to standard bytestring format
        not implemented because its not immediately evident or important to do so
        '''
        pass

    @classmethod
    def init_from_image_byte_arrays(cls, images, image_filenames=[]):
        '''
        Accepts images as list of byte arrays and optional image_filenames
        '''
        return cls(images, image_filenames)

    def get_images_as_bytestring(self):
        '''
        returns read images which is basically a bytestring, or its fundamental form
        '''
        return [image.read() for image in self.images]

    def get_images_as_gridFs(self):
        '''
        NOT IMPLEMENTED

        returns images as gridFs objects, useful for storing in a mongo database if images are large (> 16 MB)
                else recommended to store as bytestring
        '''
        return [image]

    def get_images_from_bytestrings(self):
        '''
        data is stored in subclasses typically as bytestrings so this converts them back
        to their base64 image
        '''
        return self.get_images_as_base64()

    def get_images_as_base64(self):
        '''
        encodes images as base64
        '''
        return [base64.b64encode(bytestr) for bytestr in self.images]

    def get_email_ready_format(self):
        '''
        returns images formatted as list of two-tuples of form (image_filename or 'image{idx}', image_byte_array)
        '''
        if self.image_filenames and len(self.image_filenames) > 0:
            return list(zip(self.image_filenames, self.images))
        else:
            return list(
                zip(
                    [f"image{idx+1}"
                     for idx in range(len(self.images))],
                    self.images))


class ImgProcessorJS(ImageHandler):
    '''
    Pass in a javascript formdata object as <ajaxRequest> and return images formatted as you wish

    Handles multiple images by default

when you get the request from ajax, instantiate like so:

image_handler = ImgProcessorJS(request)

the request expects only images, passing other file types will break this


    Make ajax call like so (for images only):

            function passImage() {
                    let file = document.getElementById('file').files[0]
                    var data = new FormData();
                    data.append("img", file);

                    let url = '/example'

                    $.ajax({
                            url: url,
                            data: data,
                            type: 'POST',
                            processData: false,
                            contentType: false,
                            success: function(results) {
                                    prnt(results, 'passed');
                            },
                            error: function(result) {
                                    prnt(result, 'failed')
                            }
                    });


    If passing more data than images, it will look something like this (have to serialize
    other data before adding it to the formdata obj):

            var data = new FormData();
                    var url = "/example"
                    var form_data = $('#user-form').serializeArray();
                    $.each(form_data, function (key, input) {
                                    data.append(input.name, input.value);
                    });
                    var file_data = $('#file')[0].files;
                    data.append("file", file_data[0]);

                    $.ajax({
                            url: url,
                            data: data,
                            type: 'POST',
                            processData: false,
                            contentType: false,
                            success: function(results) {
                                    $('.form-error').each(function() {
                                            $(this).text('');
                                    });
                                    if (results.errors) {
                                            for (const [key, value] of Object.entries(results.errors)) {
                                                    $(`#${key}-error`).text(value)
                                            }
                                    } else {
                                            location.reload(true);
                                    }
                            }
                    });

    '''

    def __init__(self, ajaxRequest):

        self.images = [ajaxRequest.files[key] for key in ajaxRequest.files]
        prnt(type(self.images[0]), 'python image type from ajax files')
        prnt(dir(self.images[0]), 'directory')
        prnt(self.images[0].stream, 'stream')
        self.image_filenames = [image.filename for image in self.images]
        prnt(self.image_filenames, 'image names')

        self.images = self.get_images_as_bytestring()
