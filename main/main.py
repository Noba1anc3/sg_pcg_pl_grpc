'''
@Description: 
@version: 
@Company: VIDET
@Author: ZHANG XUANRUI
@Date: 2019-06-02 20:52:11
@LastEditors: ZHANG XUANRUI
@LastEditTime: 2019-06-06 10:30:29
'''

import os
import cv2
import sys
import json
import random
import numpy as np
from vconf import Config
from logzero import logger
sys.path.append('/home/videt/dar_project/videt-dar-sg-customs-pcg-packinglist-grpc')

from v_dar_sg_customs_pcg_packinglist_grpc import about
from v_dar_sg_customs_pcg_packinglist_grpc.service.handle import Handle

class PCG_packing_list():

    def __init__(self):
        self.profile = Config(domain = about.domain, app = about.appname, env = "local").getConf()
        self.handle = Handle(self.profile)

        self.process_path = "./PCG/"
        self.folder_path = "./PCG/packing-list/"
        self.save_path = self.process_path + "_save"
        self.show_path = self.process_path + "_show"
        self.output_path = self.process_path + "_output"

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        if not os.path.exists(self.show_path):
            os.makedirs(self.show_path)
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        self.image_name_list = os.listdir(self.folder_path)
        self.image_total_num = len(self.image_name_list)

    def prepare_data(self):
        if not os.path.exists(os.path.join(self.save_path, 'image')):
            os.makedirs(os.path.join(self.save_path, 'image'))
        if not os.path.exists(os.path.join(self.save_path, 'rec')):
            os.makedirs(os.path.join(self.save_path, 'rec'))
        if not os.path.exists(os.path.join(self.save_path, 'det')):
            os.makedirs(os.path.join(self.save_path, 'det'))

        for idx, image_name in enumerate(self.image_name_list):
            if os.path.exists(os.path.join(self.save_path, 'rec', image_name.split('.')[0] + '.npy')):
                continue

            image = cv2.imread(os.path.join(self.folder_path, image_name))
            reco_result, flip_bboxes = self.handle._prepare_data(image)
            reco_result = np.array(reco_result)
            flip_bboxes = np.array(flip_bboxes)

            cv2.imwrite(os.path.join(self.save_path, 'image', image_name), image)
            np.save(os.path.join(self.save_path, 'rec', image_name.split('.')[0] + '.npy'), reco_result)
            np.save(os.path.join(self.save_path, 'det', image_name.split('.')[0] + '.npy'), flip_bboxes)

            cv2.drawContours(image, flip_bboxes, -1, (0, 0, 255), 3)
            cv2.imwrite(os.path.join(self.show_path, image_name), image)
            logger.info(image_name + "  " + str(idx) + "/" + str(self.image_total_num))
            #cv2.imshow('image', image)
            #cv2.waitKey(0)

    def show(self, image, show, save_to_folder):
        if self.handle.transform_matrix is not None:
            self.handle._transform_boxes()
        self.origin_image = image
        for item in self.handle.final_result.values():
            if isinstance(item, list):
                for item in item:
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    for commodity in item.values():
                        item_boxes = np.array(commodity['locations'])
                        if len(item_boxes) == 0:
                            continue
                        cv2.drawContours(self.origin_image, item_boxes, -1, (r, g, b), 3)
                        put_txt = ''.join(commodity['value'])
                        boxes = np.array(item_boxes)
                        centx = int(np.max(boxes[:, :, 0]))
                        centy = int(np.min(boxes[:, :, 1]))
                        self.origin_image = cv2.putText(self.origin_image, put_txt, (centx, centy),
                                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (r, g, b), 3)

            else:
                item_boxes = np.array(item['locations'])
                if len(item_boxes) == 0:
                    continue
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                cv2.drawContours(self.origin_image, item_boxes, -1, (r, g, b), 3)
                put_txt = ''.join(item['value'])
                boxes = np.array(item_boxes)
                centx = int(np.max(boxes[:, :, 0]))
                centy = int(np.min(boxes[:, :, 1]))
                self.origin_image = cv2.putText(self.origin_image, put_txt, (centx, centy),
                                                cv2.FONT_HERSHEY_SIMPLEX, 1, (r, g, b), 3)
        if show:
            cv2.imshow('PCG', cv2.resize(self.origin_image, None, None, 0.8, 0.8))
            cv2.waitKey(5)

        if save_to_folder:
                cv2.imwrite(os.path.join(self.output_path, image_name), self.origin_image)


    def run(self, image, flip_bboxes, reco_result, image_type = None,
            rectify = False, correct = False, show = False, save_to_folder = False):
        self.handle._reset_()
        self.handle.__prepare__(image, flip_bboxes, reco_result, image_type = image_type)
        self.handle.pre_process()
        self.handle.layout_extract()
        self.handle.key_info_extract(rectify, correct)
        self.handle.table_info_extract(rectify)
        self.show(image, show, save_to_folder)
        return_json = self.handle.check_json()
        return return_json

    def _read_info(self, image_name, folder_path = None):
        image = cv2.imread(os.path.join(folder_path, 'image', image_name))
        flip_bboxes = np.load(os.path.join(folder_path, 'det', image_name.split('.')[0] + '.npy'))
        reco_result = np.load(os.path.join(folder_path, 'rec', image_name.split('.')[0] + '.npy'))
        return image, flip_bboxes, reco_result


if __name__ == '__main__':
    PCG = PCG_packing_list()
    PCG.prepare_data()
    for idx, image_name in enumerate(sorted(PCG.image_name_list)):
        image, flip_bboxes, reco_result = PCG._read_info(image_name, PCG.save_path)
        return_json = PCG.handle.run(image, flip_bboxes, reco_result, image_type = 'packing_list',
                              rectify = True, correct = True, show = True, save_to_folder = True)
        with open("return.json", "w") as f:
            f.write(json.dumps(return_json))
