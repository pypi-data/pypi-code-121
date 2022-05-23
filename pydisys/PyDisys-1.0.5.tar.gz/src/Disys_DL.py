import ctypes
import sys
import splitfolders 
import os
import shutil
import numpy as np
import halcon as ha
import time


class Preprocess:

    dataset_dir = []

    def __init__(self):
        pass

    def SplitAcquisitions(self, folder_path_in, folder_path_out , split = [0.7,0.15,0.15] , move_files = False , verbose = True ) :
        if not verbose:
            sys.stdout = open(os.devnull, 'w')
        try :
            os.mkdir()
        except:
            pass    
        if len(split) == 3:
            splitfolders.ratio(folder_path_in, folder_path_out,seed=99,ratio=split,move=move_files)
        else:
            splitfolders.ratio(folder_path_in, folder_path_out,seed=99,ratio=[split[0],0.0,split[1]],move=move_files)
            shutil.rmtree(folder_path_out+r'/val')
        self.dataset_dir = folder_path_out

class Utils:
    
    @staticmethod
    def CalcolaDisparity(image_path, sogliaLaser):
        tmp = ha.read_image(image_path[0])
        domain = ha.get_domain(tmp)
        PARAM_NAME = ['min_gray','method','score_type','ambiguity_solving']
        PARAM_SEQUENCE = [sogliaLaser,'center_of_gravity','intensity','first' ]
        SheetOfLightId = ha.create_sheet_of_light_model(domain, PARAM_NAME, PARAM_SEQUENCE)
        for im_p in (image_path):
            im = ha.read_image(im_p)
            im = ha.access_channel(im,1)
            ha.measure_profile_sheet_of_light(im,SheetOfLightId,[])
        score = ha.get_sheet_of_light_result(SheetOfLightId,'score')
        disparity = ha.get_sheet_of_light_result(SheetOfLightId,'disparity')
        ha.clear_sheet_of_light_model(SheetOfLightId)
        return disparity,score    

    @staticmethod
    def getBlobsFromScore(input_score_image,threshold_score_image):
        tmp = ha.threshold(input_score_image,threshold_score_image,255)
        connected_regions = ha.connection(tmp)
        tmp = ha.fill_up(connected_regions)
        tmp = ha.select_shape(tmp,'area','and',50,10e10)
        return ha.union1(tmp)

    # def ClassifyBlobs(input_labelled_image):
    #     regions = ha.threshold(input_labelled_image,0,255)
    #     regions = ha.connection(regions)
    #     regions = ha.fill_up(regions)
    #     regions = ha.select_shape(regions,'area','and',150,1e10)
        
    #     #mean_gray = ha.gray_features(regions,input_labelled_image,'mean')

    #     reg_mdf = ha.select_gray(regions,input_labelled_image,'median','and',252,255)
    #     reg_nomdf = ha.select_gray(regions,input_labelled_image,'median','and',125,129)
    #     reg_sfondo = ha.select_gray(regions,input_labelled_image,'median','and',0,10)
    #     out_im = ha.copy_image(input_labelled_image)
    #     ha.overpaint_region(out_im,reg_mdf,255,'fill')
    #     ha.overpaint_region(out_im,reg_nomdf,128,'fill')
    #     #ha.overpaint_region(out_im,reg_sfondo,0,'fill')
    #     return out_im
    @staticmethod
    def ClassifyBlobs(input_labelled_image, erode = False):
        regions = ha.threshold(input_labelled_image,0,255)
        regions = ha.connection(regions)
        regions = ha.fill_up(regions)
        regions_analysis = ha.select_shape(regions,'area','and',150,1e10)
        regions = ha.select_shape(regions,'area','and',150,1e10)
        if erode:
            st_el = ha.gen_rectangle1(0,0,0,31)
            regions_analysis = ha.erosion1(regions,st_el,1)
            
        area = np.array(ha.area_center(regions_analysis)[0])
        
        r,g,b = ha.decompose3(input_labelled_image)

        r_area_vals = np.array(ha.area_center_gray(regions_analysis, r )[0])
        g_area_vals = np.array(ha.area_center_gray(regions_analysis, g )[0])
        b_area_vals = np.array(ha.area_center_gray(regions_analysis, b )[0])

        r_o,g_o,b_o = ha.decompose3(input_labelled_image)
        ind  = np.argmax(np.array([r_area_vals,g_area_vals,b_area_vals]),axis=0)
        mdf_ind = np.where(ind==0)[0]+1
        no_mdf_ind = np.where(ind==1)[0]+1
        area_ind = np.where(area == 0)[0]+1
        
        if mdf_ind.size != 0:
            mdf_reg = ha.select_obj(regions,mdf_ind.tolist())
            ha.overpaint_region(r_o,mdf_reg,255,'fill')
            ha.overpaint_region(g_o,mdf_reg,0,'fill')
            ha.overpaint_region(b_o,mdf_reg,0,'fill')
        if no_mdf_ind.size != 0:
            no_mdf_reg = ha.select_obj(regions,no_mdf_ind.tolist())
            ha.overpaint_region(g_o,no_mdf_reg,255,'fill')
            ha.overpaint_region(r_o,no_mdf_reg,0,'fill')
            ha.overpaint_region(b_o,no_mdf_reg,0,'fill')
        if area_ind.size != 0:
            empty_area = ha.select_obj(regions,area_ind.tolist())
            not_empty_area = ha.complement(ha.union1(empty_area))
            r_o = ha.crop_domain(ha.reduce_domain(r_o,not_empty_area))
            g_o = ha.crop_domain(ha.reduce_domain(g_o,not_empty_area))
            b_o = ha.crop_domain(ha.reduce_domain(b_o,not_empty_area))
        
        out_im = ha.compose3(r_o,g_o,b_o)
        #ha.overpaint_region(out_im,reg_sfondo,0,'fill')
        return out_im


    @staticmethod
    def doInference(test_generator,model):
        elapsed_times = []
        scores = np.empty
        vals = np.empty
        allClasses = np.empty
        N = test_generator.__len__()
        for Id in range(0,N):
            print("Batch ", Id, "/", N, end="\r")
            start = time.time()
            x = next(test_generator)
            prediction_scores = model.predict_on_batch(x)
            tmp = np.array(prediction_scores)
            stop = time.time()
            elapsed_times.append(stop-start)
            scores=np.append(scores,np.argmax(tmp,axis=1))
            vals=np.append(vals,np.max(tmp,axis=1))
            allClasses = np.append(allClasses,tmp)
        scores = np.delete(scores,0)
        vals = np.delete(vals,0)
        allClasses = np.delete(allClasses,0)
        print("average elapsed seconds per inference: ", sum(elapsed_times)/len(elapsed_times))
        return scores,vals,allClasses
    @staticmethod
    def hImage2nparray(input_hImage):
        channels = ha.count_channels(input_hImage)[0]
        if channels == 3:
            images = ha.decompose3(input_hImage)
            width, height = ha.get_image_size(input_hImage)
            v = np.zeros((height[0],width[0],3))
            k = 0
            for im in images:
                ptr_struct = ha.get_image_pointer1(im)
                ptr = ptr_struct[0]
                im_type = ptr_struct[1]
                width = ptr_struct[2]
                height = ptr_struct[3]

                #aggiungere i vari data type al bisogno 
                image_type = ctypes.c_byte
                if im_type[0] == 'real':
                    image_type = ctypes.c_float

                v[:,:,k] = np.ctypeslib.as_array(ctypes.cast(ptr[0],ctypes.POINTER(image_type)),shape=(height[0],width[0]))
                k +=1
        else :
            ptr_struct = ha.get_image_pointer1(input_hImage)
            ptr = ptr_struct[0]
            im_type = ptr_struct[1]
            width = ptr_struct[2]
            height = ptr_struct[3]

            #aggiungere i vari data type al bisogno 
            image_type = ctypes.c_byte
            if im_type[0] == 'real':
                image_type = ctypes.c_float

            v = np.ctypeslib.as_array(ctypes.cast(ptr[0],ctypes.POINTER(image_type)),shape=(height[0],width[0]))
        return v
    @staticmethod
    def nparray2HImage(input_nparray):
        tipo = input_nparray.dtype
        #print(tipo.name)
        if tipo.name == 'int32' or tipo.name == 'uint8':
            ic = np.array(input_nparray,dtype=np.int32)
            out_t = 'int4'
        elif tipo.name == 'float32' or tipo.name == 'object' :
            ic = np.array(input_nparray,dtype=np.float32)
            out_t = 'real'
        elif tipo.name == 'int8' :
            ic = np.array(input_nparray,dtype=np.int8)
            out_t = 'byte'

        if input_nparray.ndim == 3:
            width = np.size(ic,2)
            height = np.size(ic,1)
            ## Magari si può fare in altro modo
            pointer_r = ic[0,:,:].__array_interface__['data'][0]
            pointer_g = ic[1,:,:].__array_interface__['data'][0]
            pointer_b = ic[2,:,:].__array_interface__['data'][0]
            new_im_r = ha.gen_image1(out_t,width,height,pointer_r)
            new_im_g = ha.gen_image1(out_t,width,height,pointer_g)
            new_im_b = ha.gen_image1(out_t,width,height,pointer_b)
            new_im = ha.compose3(new_im_r,new_im_g,new_im_b)
        else:
            width = np.size(ic,1)
            height = np.size(ic,0)
            pointer = ic.__array_interface__['data'][0]
            #print(out_t)
            new_im = ha.gen_image1(out_t,width,height,pointer)
        return new_im

    @staticmethod
    def getImageToPlot(inputImage):
        tmp = ha.full_domain(inputImage)
        w,h = ha.get_image_size(tmp)
        domain = ha.get_domain(tmp)
        r,c = ha.get_region_points(domain)
        gv = ha.get_grayval(tmp,r,c)
        im = np.array(gv)
        im = np.resize(im,(h[0],w[0]))
        return im

    @staticmethod
    def CreateHImageFromNParray(input_array):
        w = np.size(input_array,1)
        h = np.size(input_array,0)
        tmp = ha.gen_image_const('real',w,h)
        vals = np.resize(input_array,(w*h,1)).transpose().tolist()[0]
        tmp = ha.full_domain(tmp)
        domain = ha.get_domain(tmp)
        r,c = ha.get_region_points(domain)
        ha.set_grayval(tmp,r,c,vals)
        out = ha.scale_image_max(tmp)
        return out


    @staticmethod
    def getRGBFromAllClasses(input_array_of_classes,step_window,w,h):
        tmp = np.tile(input_array_of_classes.transpose(),(step_window,1)).transpose()
        r_prova = np.reshape(tmp[0:-2:3,:],(h[0],w[0]))
        g_prova = np.reshape(tmp[1:-1:3,:],(h[0],w[0]))
        b_prova = np.reshape(tmp[2:len(tmp):3,:],(h[0],w[0]))
        rgb = np.array([r_prova,g_prova,b_prova])
        return rgb

    @staticmethod
    def getRGBFromBestClassValues(input_array_of_best_class, input_array_best_classVal,step_window,w,h):
        r_vals = np.where(input_array_of_best_class == 2)[0]
        g_vals = np.where(input_array_of_best_class == 1)[0]
        b_vals = np.where(input_array_of_best_class == 0)[0]

        ## Seleziono dall 'altro array i vari valori 

        tmp2 = input_array_best_classVal.copy()
        tmp3 = input_array_best_classVal.copy()
        tmp4 = input_array_best_classVal.copy()

        tmp2[g_vals] = 0
        tmp2[b_vals] = 0
        r_im = tmp2 

        tmp3[r_vals] = 0
        tmp3[b_vals] = 0
        g_im = tmp3 

        tmp4[g_vals] = 0
        tmp4[r_vals] = 0
        b_im = tmp4 

        r_tmp = np.tile(r_im.transpose(),(step_window,1)).transpose()
        r = np.reshape(r_tmp,(h[0],w[0]))
        g_tmp = np.tile(g_im.transpose(),(step_window,1)).transpose()
        g = np.reshape(g_tmp,(h[0],w[0]))
        b_tmp = np.tile(b_im.transpose(),(step_window,1)).transpose()
        b = np.reshape(b_tmp,(h[0],w[0]))

        rgb = np.array([r,g,b])
        return rgb

    @staticmethod
    def CropImages(imagePath, window_height, window_width, window_step):
        image_files = ha.list_files(imagePath,'files')
        h_images = ha.read_image(image_files)
        images = []
        for im in h_images:
            images.append(ha.himage_as_numpy_array(im))
        width = np.size(images[0],1)
        height = np.size(images[0],0)
        cropped = []
        for im in images:
            im_proc = np.pad(im, ((0,0),(int(window_width/2),int(window_width/2))),mode='minimum')
            for i in range(0,int(width),window_step):
                cropped.append(im_proc[0:window_height,i:i+window_width])
        return cropped
    # @staticmethod
    # def DataFlowForInference(images , batch_size ):
    #     tensore = tf.convert_to_tensor(images)
    #     x = tf.expand_dims(tensore, axis =3)
    #     tensore = []
    #     datagen_kwargs = dict(rescale=1./255)                
    #     test_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    #                     **datagen_kwargs).flow(x,batch_size=batch_size,shuffle=False)
    #     return test_generator

    @staticmethod
    def OutScore(inputImage):
        r,g,b = ha.decompose3(inputImage)
        domain = ha.threshold(inputImage,0,255)
        area_mdf = ha.area_center_gray(domain,r)[0][0]
        area_no_mdf = ha.area_center_gray(domain,g)[0][0]

        area_tot = area_mdf+area_no_mdf
        mdf = area_mdf/area_tot 
        no_mdf = area_no_mdf/area_tot 

        return mdf,no_mdf


