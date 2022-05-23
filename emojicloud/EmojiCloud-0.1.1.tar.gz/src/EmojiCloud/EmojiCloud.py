import os
from PIL import Image
import matplotlib.pyplot as plt
import copy
import math
import collections
import EmojiCloud

def distance_between_two_points(x_1, y_1, x_2, y_2):
    """calculate the distance between two points

    Args:
        x_1 (float): x of the first point
        y_1 (float): y of the first point
        x_2 (float): x of the second point
        y_2 (float): y of the second point

    Returns:
        float: the distance between two points
    """
    if (x_1 != x_2):
        dist = math.sqrt((x_1 - x_2)**2 + (y_1 - y_2)**2)
    else:
        dist = math.fabs(y_1 - y_2)
    return dist

def sort_dictionary_by_value(dict_sort, reverse = True):
    """sort dictionary based on the value

    Args:
        dict_sort (dictionary): a dictionary to be sorted
        reverse (bool, optional): in a reverse order. Defaults to True.

    Returns:
        list of tuple (key, value): a list of sorted tuple
    """
    list_tuple_sorted = [(k, dict_sort[k]) for k in sorted(dict_sort, key=dict_sort.get, reverse = reverse)]
    return list_tuple_sorted

def parse_image_by_array(im):
    """parse the given image 

    Args:
        im (2D list): the image in 2D array with each cell of RGBA

    Returns:
        width: the image width
        height: the image height
        dict_opacity: key: coordinate, value: the RGB value
    """    
    # read image
    im_data = im.getdata()
    width, height = im.size
    # identify transparent pixels
    dict_opacity = {} # key: coordinate, value: RGB value
    for index, pixel in enumerate(im_data):
        x = index % width
        y = int(index / width)
        # opacity coordinates along with RGB values
        if (pixel[3] != 0):
            dict_opacity[tuple([x, y])] = pixel
    return width, height, dict_opacity

def remove_pixel_outside_bb(im, thold_alpha):
    """remove all pixels outside the bounding box

    Args:
        im (2D list): the image in 2D array with each cell of RGBA
        thold_alpha (float): the threshold to distinguish white and non-white colors

    Returns:
        im_dense: the new image after removing bounding box
    """
    # read image
    im_data = im.getdata()
    width, height = im.size
    dict_pixel = {} # key: coordinate, value: RGB value 
    # check pixels
    for index, pixel in enumerate(im_data):
        x = index % width
        y = int (index / width)
        dict_pixel[tuple([x, y])] = pixel
    # remove transparent rows 
    list_row = []
    for x in range(width):
        flag = True
        for y in range(height):
            if (dict_pixel[tuple([x, y])][3] >= thold_alpha):
                flag = False
                break 
        if (not flag):
            list_row.append([dict_pixel[tuple([x, y])] for y in range(height)])
    # remove transparent columns 
    column_count = len(list_row[0])
    list_column = []
    for y in range(column_count):
        flag = True
        for row in list_row:
            if (row[y][3] >= thold_alpha):
                flag = False
                break
        if (not flag):
            list_column.append([row[y] for row in list_row])
    # reorganize new image
    width = len(list_column[0])
    height = len(list_column)
    im_dense = Image.new('RGBA', (width, height))
    for i in range (width):
        for j in range (height):
            im_dense.putpixel((i, j), list_column[j][i])
    return im_dense

def resize_img_based_weight(im_read, weight):
    """resize original image based on its weight

    Args:
        im_read (2D list): the image in 2D array with each cell of RGBA
        weight (float): weight of the image 

    Returns:
        im_resize (2D list): the image in 2D array with each cell of RGBA: the image width
    """    
    width, height = im_read.getdata().size
    im_resize = im_read.resize((int(width*weight), int(height*weight)), Image.ANTIALIAS)
    return im_resize

def check_point_within_ellipse(center_x, center_y, x, y, radius_x, radius_y):
    """check whether a point is within a given ellipse

    Args:
        center_x (int): the center x of the ellipse
        center_y (int): the center y of the ellipse
        x (int): the x of point 
        y (int): the y of the point
        radius_x (int): the radius of x-axis 
        radius_y (int): the radius of y-axis

    Returns:
        bool: True or False
    """    
    # ellipse with the given point
    p = ((math.pow((x - center_x), 2) / math.pow(radius_x, 2)) + (math.pow((y - center_y), 2) / math.pow(radius_y, 2)))
    if (p <= 1):
        return True
    else:
        return False

class OrderedSet(collections.Set):
    def __init__(self, iterable=()):
        self.d = collections.OrderedDict.fromkeys(iterable)
    def __len__(self):
        return len(self.d)
    def __contains__(self, element):
        return element in self.d
    def __iter__(self):
        return iter(self.d)

# ellipse canvas 
def create_ellipse_canvas(canvas_w = 72*10, canvas_h = 72*5, canvas_color='white'):
    """create a ellipse canvas where all pixels are available to be plotted on

    Args:
        canvas_w (int, optional): the width of canvas in pixel. Defaults to 72*10.
        canvas_h (int, optional): the height of canvas in pixel. Defaults to 72*10.
        canvas_color: the color of canvas

    Returns:
        canvas_img: the image of canvas
        map_occupied: a 2D list of which pixels are available to be plotted on
        canvas_area: the area of the canvas
        canvas_center_x: the center x of the canvas
        canvas_center_y: the center y of the canvas
    """    
    canvas_img = Image.new('RGBA', (canvas_w, canvas_h), color=canvas_color)
    canvas_center_x, canvas_center_y = int(canvas_w/2), int(canvas_h/2)
    map_occupied = [[1 for i in range(canvas_h)] for j in range(canvas_w)]
    for x in range(canvas_w):
        for y in range(canvas_h):
            flag = check_point_within_ellipse(canvas_center_x, canvas_center_y, x, y, canvas_w/2, canvas_h/2)
            if (flag):
                map_occupied[x][y] = 0
    canvas_area = (canvas_w/2) * (canvas_h/2) * math.pi
    return canvas_img, map_occupied, canvas_area, canvas_center_x, canvas_center_y

# rectangle canvas 
def create_rectangle_canvas(canvas_w = 72*10, canvas_h = 72*10, canvas_color='white'):
    """create a rectangle canvas where all pixels are available to be plotted on

    Args:
        canvas_w (int, optional): the width of canvas in pixel. Defaults to 72*10.
        canvas_h (int, optional): the height of canvas in pixel. Defaults to 72*10.
        canvas_color: the color of canvas

    Returns:
        canvas_img: the image of canvas
        map_occupied: a 2D list of which pixels are available to be plotted on
        canvas_area: the area of the canvas
        canvas_center_x: the center x of the canvas
        canvas_center_y: the center y of the canvas
    """    
    canvas_img = Image.new('RGBA', (canvas_w, canvas_h), color=canvas_color)
    canvas_center_x, canvas_center_y = int(canvas_w/2), int(canvas_h/2)
    map_occupied = [[0 for i in range(canvas_h)] for j in range(canvas_w)]
    canvas_area = canvas_w * canvas_h
    return canvas_img, map_occupied, canvas_area, canvas_center_x, canvas_center_y

def calculate_contour(im, thold_alpha=10):
    """calculate the contour of the given image

    Args:
        im (2D list): the image in 2D array with each cell of RGBA
        thold_alpha: the threshold to distinguish the colors on the contour and outside the contour

    Returns:
        list_contour: the list of (x, y) on the contour
    """    
    # read image
    img_data = im.getdata()
    width, height = im.size
    dict_pixel = {} # key: coordinate, value: RGB value 
    # check pixels
    for index, pixel in enumerate(img_data):
        x = index % width
        y = int (index / width)
        dict_pixel[tuple([x, y])] = pixel
    # identify contour by row 
    list_contour = []
    for x in range(width):
        prev_alpha = dict_pixel[tuple([x, 0])][3]
        for y in range(1, height):
            if (abs(dict_pixel[tuple([x, y])][3] - prev_alpha) > thold_alpha):
                list_contour.append(tuple([x, y]))
                prev_alpha = dict_pixel[tuple([x, y])][3]
    # identify contour by column
    for y in range(1, height):
        prev_alpha = dict_pixel[tuple([0, y])][3]
        for x in range(width):
            if (abs(dict_pixel[tuple([x, y])][3] - prev_alpha) > thold_alpha):
                list_contour.append(tuple([x, y]))
                prev_alpha = dict_pixel[tuple([x, y])][3]
    return list_contour

# masked image canvas
def create_masked_canvas(img_mask, contour_width, contour_color, thold_alpha_contour=10, thold_alpha_bb=0):
    """create a masked canvas

    Args:
        img_mask (path of a masked image): the path of a masked image 
        contour_width: the contour width
        contour_color: the contour color
        thold_alpha_contour: the threshold to distinguish the colors on the contour and outside the contour
        thold_alpha_bb: the threshold to distinguish white and non-white colors for bounding box detection

    Returns:
        canvas_img: the image of canvas
        map_occupied: a 2D list of which pixels are available to be plotted on
        canvas_area: the area of the canvas
        canvas_center_x: the center x of the canvas
        canvas_center_y: the center y of the canvas
    """
    # remove pixel outside bounding box 
    im_read = Image.open(img_mask)
    im = im_read.convert('RGBA')
    img_mask_within_bb = remove_pixel_outside_bb(im, thold_alpha_bb)
    # parse masked image
    canvas_w, canvas_h, dict_opacity = parse_image_by_array(img_mask_within_bb)
    canvas_w = canvas_w + contour_width*2
    canvas_h = canvas_h + contour_width*2
    canvas_img = Image.new('RGBA', (canvas_w, canvas_h), color="white")
    map_occupied = [[1 for i in range(canvas_h)] for j in range(canvas_w)]
    # set pixels in the mask image as unoccupied
    for (x, y) in dict_opacity:
        map_occupied[x][y] = 0
    # process contour 
    list_contour = calculate_contour(img_mask_within_bb, thold_alpha_contour)
    # contour width 
    for (x, y) in list_contour:
        for i in range(contour_width):
            for j in range(contour_width):
                canvas_img.putpixel((x + i, y + j), contour_color)
                map_occupied[x + i][y + j] = 1
    canvas_center_x, canvas_center_y = int(canvas_w/2), int(canvas_h/2)
    canvas_area = len(dict_opacity)
    return canvas_img, map_occupied, canvas_area, canvas_center_x, canvas_center_y, canvas_w, canvas_h

def calculate_sorted_canvas_pix_for_plotting(canvas_w, canvas_h, map_occupied, canvas_center_x, canvas_center_y):
    """calculate a sorted list of canvas pixels based its distance to the canvas center point

    Args:
        canvas_w (int): the canvas width
        canvas_h (int): the canvas height
        map_occupied (list): a 2D list of whether the pixel is occupied or not 
        canvas_center_x (float): the center x of the canvas
        canvas_center_y (float): the center y of the canvas

    Returns:
        list_canvas_pix: a list of tuple (x,y) sorted by its distance to the canvas center
    """
    # points to be checked in an order determined by its distance from the center point of the image center 
    dict_dist_canvas_center = {} # key: (x, y), value: the distance to the center of canvas
    for x in range(canvas_w):
        for y in range(canvas_h):
            if (map_occupied[x][y] == 0):
                dist = distance_between_two_points(x, y, canvas_center_x, canvas_center_y)
                dict_dist_canvas_center[(x, y)] = dist
    list_canvas_pix_dist = sort_dictionary_by_value(dict_dist_canvas_center, reverse = False)
    list_canvas_pix = [x_y for (x_y, dist) in list_canvas_pix_dist]
    return list_canvas_pix

def rename_emoji_image_in_unicode(dict_weight):
    """rename emoji image name in unicode 

    Args:
        dict_weight (dict): key: emoji image name in unicode, value: emoji weight 

    Returns:
        dict_rename (dict): key: renamed emoji image in unicode, value: emoji weight 
    """
    dict_rename = {}
    for im_name in dict_weight:
        im_rename = im_name.upper()
        if '.PNG' not in im_rename:
            im_rename += '.PNG'
        if 'U+' not in im_rename:
            im_rename = 'U+' + '-U+'.join(im_rename.split('-'))
        dict_rename[im_rename] = dict_weight[im_name]
    return dict_rename

def generate_resized_emoji_images(path_img_raw, dict_weight, canvas_area, dict_customized, relax_ratio = 1.5):
    """generate the resized emoji images based on weights

    Args:
        path_img_raw (string): the path of raw emojis 
        dict_weight (dict): key: emoji image name in unicode, value: emoji weight 
        canvas_area (float): the canvas area 
        dict_customized (dict): key: emoji image name in unicode, value: the path of customized emoji image
        relax_ratio (float, optional): control the plotting sparsity. Defaults to 1.5.

    Returns:
        list_sorted_emoji: a list of sorted emojis by their weights
        list_resize_img: a list of resize image array 
    """
    # process emoji image name in unicode 
    dict_weight = rename_emoji_image_in_unicode(dict_weight)
    dict_customized = rename_emoji_image_in_unicode(dict_customized)
    # normalize weight 
    weight_sum = sum([dict_weight[im_name] for im_name in dict_weight])
    for im_name in dict_weight:
        dict_weight[im_name] = dict_weight[im_name]/weight_sum
    # calculate zoom in/out ratio
    norm_area_sum = 0
    for im_name in dict_weight:
        if im_name not in dict_customized:
            im_read = Image.open(EmojiCloud.__path__[0] + '/' + os.path.join(path_img_raw, im_name))
        else:
            im_read = Image.open(dict_customized[im_name])
        width, height = im_read.getdata().size
        norm_area_sum += width*height*(dict_weight[im_name]**2)
    zoom_ratio = math.sqrt(canvas_area/norm_area_sum)/relax_ratio
    for im_name in dict_weight:
        dict_weight[im_name] = dict_weight[im_name]*zoom_ratio
    list_sorted_emoji = sort_dictionary_by_value(dict_weight, reverse = True)
    # resize images
    list_resize_img = []
    for item in list_sorted_emoji:
        im_name, weight = item[0], item[1]
        if im_name not in dict_customized:
            im_read = Image.open(EmojiCloud.__path__[0] + '/' + os.path.join(path_img_raw, im_name))
        else:
            im_read = Image.open(dict_customized[im_name])
        im_read = im_read.convert('RGBA')
        resize_img = resize_img_based_weight(im_read, weight)
        list_resize_img.append(resize_img)
    return list_sorted_emoji, list_resize_img

def plot_emoji_cloud_given_relax_ratio(path_img_raw, canvas_img, canvas_w, canvas_h, canvas_area, dict_weight, list_canvas_pix, map_occupied, dict_customized, thold_alpha_bb, relax_ratio):
    """plot emoji cloud

    Args:
        path_img_raw (string): the path of raw emoji images 
        canvas_img: the image of canvas
        canvas_w (int): the canvas width
        canvas_h (int): the canvas height
        canvas_area: the area of canvas 
        dict_weight (dict): key: emoji image name in unicode, value: weight
        list_canvas_pix (list): a list of tuple (x,y) sorted by its distance to the canvas center
        map_occupied (list): a 2D list of whether the pixel is occupied or not 
        dict_customized (dict): key: emoji image name in unicode, value: the path of customized emoji image
        thold_alpha_bb: the threshold to distinguish white and non-white colors for bounding box detection 
        relax_ratio (float): the ratio >=1, controlling the sparsity of emoji plotting

    Returns:
        canvas_img: the final image of canvas
        count_plot: the count of plotted emojis 
    """
    # new_list_canvas_pix = list_canvas_pix.copy()
    new_list_canvas_pix = copy.deepcopy(list_canvas_pix)
    # new_canvas_img = canvas_img.copy()
    new_canvas_img = copy.deepcopy(canvas_img)
    # new_map_occupied = map_occupied.copy()
    new_map_occupied = copy.deepcopy(map_occupied)
    list_sorted_emoji, list_resize_img = generate_resized_emoji_images(path_img_raw, dict_weight, canvas_area, dict_customized, relax_ratio)
    # plot each emoji 
    count_plot = 0 
    for index, item in enumerate(list_sorted_emoji):
        # fail to plot the last emoji image 
        if (index != count_plot):
            break 
        im_name, weight = item[0], item[1]
        # remove pixel outside bounding box 
        im = list_resize_img[index]
        img_within_bb = remove_pixel_outside_bb(im, thold_alpha_bb)
        # parse emoji image 
        img_width, img_height, dict_opacity = parse_image_by_array(img_within_bb)
        # get the center point of the emoji image 
        list_x = []
        list_y = []
        for (x, y) in dict_opacity:
            list_x.append(x)
            list_y.append(y)
        center = sum(list_x)/len(list_x), sum(list_y)/len(list_y)
        img_center_x = int(center[0])
        img_center_y = int(center[1])
        # sort opacity point by distant to the center point
        dict_dist_img_center = {} # key: point, value: point to the image center 
        for (x, y) in dict_opacity:
            # dist = distance_between_two_points(x, y, img_width/2, img_height/2)
            dist = distance_between_two_points(x, y, img_center_x, img_center_y)
            dict_dist_img_center[(x, y)] = dist
        list_img_pix_dist = sort_dictionary_by_value(dict_dist_img_center, reverse = True)
        list_img_pix = [x_y for (x_y, dist) in list_img_pix_dist]
        # check the possibility of each pixel starting from the center 
        for x_y in new_list_canvas_pix:
            canvas_x, canvas_y = x_y
            # check all points 
            flag = True
            for (x, y) in list_img_pix:
                # adding offset 
                offset_x = x - img_center_x
                offset_y = y - img_center_y
                # candidate x, y on canvas
                candidate_x = canvas_x + offset_x
                candidate_y = canvas_y + offset_y
                # check validity
                if (candidate_x < canvas_w and candidate_x >= 0 and candidate_y < canvas_h and candidate_y >= 0):
                    # the pixel on canvas has been occupied
                    if (new_map_occupied[canvas_x + offset_x][canvas_y + offset_y] == 1):
                        flag = False
                        break
                # out of the canvas 
                else:
                    flag = False
                    break
            # plot emoji image
            if (flag):
                list_occupied = []
                for (x, y) in dict_opacity:
                    # adding offset 
                    offset_x = x - img_center_x
                    offset_y = y - img_center_y
                    # candidate x, y on canvas
                    candidate_x = canvas_x + offset_x
                    candidate_y = canvas_y + offset_y
                    # plot the emoji
                    new_canvas_img.putpixel((candidate_x, candidate_y), dict_opacity[(x, y)])
                    new_map_occupied[candidate_x][candidate_y] = 1
                    list_occupied.append((candidate_x, candidate_y))
                # continue processing the next emoji 
                count_plot += 1
                break
            else:
                list_occupied = []
        # remove occupied tuple
        new_list_canvas_pix = list(OrderedSet(new_list_canvas_pix) - OrderedSet(list_occupied))
    return new_canvas_img, count_plot

def plot_dense_emoji_cloud(canvas_w, canvas_h, canvas_area, map_occupied, canvas_center_x, canvas_center_y, path_img_raw, saved_emoji_cloud_name, canvas_img, dict_weight, dict_customized, thold_alpha_bb, num_try=20, step_size=0.1):
    """plot dense emoji cloud

    Args:
        canvas_w (int): the canvas width
        canvas_h (int): the canvas height
        canvas_area: the area of canvas 
        map_occupied (list): a 2D list of whether the pixel is occupied or not 
        canvas_center_x (float): the center x of the canvas
        canvas_center_y (float): the center y of the canvas
        path_img_raw (string): the path of raw emoji images 
        saved_emoji_cloud_name (string): the name of the saved emoji cloud image  
        canvas_img: the image of canvas
        dict_weight (dict): key: emoji image name in unicode, value: weight
        dict_customized (dict): key: emoji image name in unicode, value: the path of customized emoji image
        thold_alpha_bb: the threshold to distinguish white and non-white colors for bounding box detection 
        num_try: number of attempts to increase the relaxed ratio of emoji images 
        step_size: the step size of increase the relaxed ratio of emoji images 
    """
    # a sorted list of available pixel positions for plotting
    list_canvas_pix = calculate_sorted_canvas_pix_for_plotting(canvas_w, canvas_h, map_occupied, canvas_center_x, canvas_center_y)
    # plot emoji cloud with an increasing relax_ratio with a fixed step size
    for i in range(num_try):
        relax_ratio = 1 + step_size*i
        canvas_img_plot, count_plot = plot_emoji_cloud_given_relax_ratio(path_img_raw, canvas_img, canvas_w, canvas_h, canvas_area, dict_weight, list_canvas_pix, map_occupied, dict_customized, thold_alpha_bb, relax_ratio)
        # plot all emojis successfully 
        if (count_plot == len(dict_weight)):
            # show emoji cloud 
            plt.imshow(canvas_img_plot)
            plt.show()
            # save emoji cloud
            canvas_img_plot.save(saved_emoji_cloud_name)
            break 

def plot_masked_canvas(img_mask, thold_alpha_contour, contour_width, contour_color, emoji_vendor, dict_weight, saved_emoji_cloud_name, dict_customized={}, thold_alpha_bb=4):
    """plot emoji cloud with masked canvas

    Args:
        img_mask (string): the masked image
        thold_alpha_contour (int): the threshold of alpha value to detect contour of a png image 
        contour_width (int): the contour width 
        contour_color (RGBA): the contour color 
        emoji_vendor (string): can be one of Apple, Google, Meta, Windows, Twitter, JoyPixels, and Samsung
        dict_weight (dict): key: emoji image name in unicode, value: weight
        saved_emoji_cloud_name (string): the name of the saved emoji cloud image  
        dict_customized (dict): key: emoji image name in unicode, value: the path of customized emoji image
        thold_alpha_bb: the threshold to distinguish white and non-white colors for bounding box detection 
    """    
    canvas_img, map_occupied, canvas_area, canvas_center_x, canvas_center_y, canvas_w, canvas_h = create_masked_canvas(img_mask, contour_width, contour_color, thold_alpha_contour, thold_alpha_bb)
    dict_vendor = {'Apple':'Appl', 'Google':'Goog', 'Meta':'FB', 'Windows':'Wind', 'Twitter':'Twtr', 'JoyPixels':'Joy', 'Samsung':'Sams'}
    path_img_raw = 'data/' + dict_vendor[emoji_vendor] # path of raw emojis
    plot_dense_emoji_cloud(canvas_w, canvas_h, canvas_area, map_occupied, canvas_center_x, canvas_center_y, path_img_raw, saved_emoji_cloud_name, canvas_img, dict_weight, dict_customized, thold_alpha_bb, num_try=20, step_size=0.1)

def plot_rectangle_canvas(canvas_w, canvas_h, emoji_vendor, dict_weight, saved_emoji_cloud_name, dict_customized={}, canvas_color='white', thold_alpha_bb=4):
    """plot rectangle canvas 

    Args:
        canvas_w (int): the canvas width
        canvas_h (int): the canvas height
        emoji_vendor (string): can be one of Apple, Google, Meta, Windows, Twitter, JoyPixels, and Samsung
        dict_weight (dict): key: emoji image name in unicode, value: weight
        saved_emoji_cloud_name (string): the name of the saved emoji cloud image  
        dict_customized (dict): key: emoji image name in unicode, value: the path of customized emoji image
        canvas_color: the color of canvas
        thold_alpha_bb: the threshold to distinguish white and non-white colors for bounding box detection 
    """    
    canvas_img, map_occupied, canvas_area, canvas_center_x, canvas_center_y = create_rectangle_canvas(canvas_w, canvas_h, canvas_color)
    dict_vendor = {'Apple':'Appl', 'Google':'Goog', 'Meta':'FB', 'Windows':'Wind', 'Twitter':'Twtr', 'JoyPixels':'Joy', 'Samsung':'Sams'}
    path_img_raw = 'data/' + dict_vendor[emoji_vendor] # path of raw emojis
    plot_dense_emoji_cloud(canvas_w, canvas_h, canvas_area, map_occupied, canvas_center_x, canvas_center_y, path_img_raw, saved_emoji_cloud_name, canvas_img, dict_weight, dict_customized, thold_alpha_bb, num_try=20, step_size=0.1)

def plot_ellipse_canvas(canvas_w, canvas_h, emoji_vendor, dict_weight, saved_emoji_cloud_name, dict_customized={}, canvas_color='white', thold_alpha_bb=4):
    """plot ellipse canvas 

    Args:
        canvas_w (int): the canvas width
        canvas_h (int): the canvas height
        emoji_vendor (string): can be one of Apple, Google, Meta, Windows, Twitter, JoyPixels, and Samsung
        dict_weight (dict): key: emoji image name in unicode, value: weight
        saved_emoji_cloud_name (string): the name of the saved emoji cloud image  
        dict_customized (dict): key: emoji image name in unicode, value: the path of customized emoji image
        canvas_color: the color of canvas
        thold_alpha_bb: the threshold to distinguish white and non-white colors for bounding box detection 
    """    
    canvas_img, map_occupied, canvas_area, canvas_center_x, canvas_center_y = create_ellipse_canvas(canvas_w, canvas_h, canvas_color)
    dict_vendor = {'Apple':'Appl', 'Google':'Goog', 'Meta':'FB', 'Windows':'Wind', 'Twitter':'Twtr', 'JoyPixels':'Joy', 'Samsung':'Sams'}
    path_img_raw = 'data/' + dict_vendor[emoji_vendor] # path of raw emojis
    plot_dense_emoji_cloud(canvas_w, canvas_h, canvas_area, map_occupied, canvas_center_x, canvas_center_y, path_img_raw, saved_emoji_cloud_name, canvas_img, dict_weight, dict_customized, thold_alpha_bb, num_try=20, step_size=0.1)

