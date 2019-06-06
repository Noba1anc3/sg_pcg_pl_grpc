'''
@Description: 
@version: 
@Company: VIDET
@Author: ZHOUZHAO
@Date: 2019-01-21 17:34:20
@LastEditors: ZHANGXUANRUI
@LastEditTime: 2019-06-06 10:30:29
'''

import cv2
from copy import deepcopy
import json
import logging
import sys
import itertools
import numpy as np

from v_dar_tools.business_tool.business_logic import BusinessLogic
from v_dar_tools.box_tool.sort_box import sort_box_by_row
from v_dar_tools.text_tool.lcs import lcs


class Handle(BusinessLogic):

    def __init__(self, business_config):
        BusinessLogic.__init__(self, business_config)

    # def _pl_shipper_check(self, sorted_recos):
    #     if sorted_recos[0] == 'PCG Trading LLC' and sorted_recos[1] == 'c/o Converge Asia Pte Ltd' and sorted_recos[
    #         2] == '20 Toh Guan Road' and sorted_recos[3] == '#06-00, CJ Logistics Building' and sorted_recos[
    #         4] == 'Singapore 608839':
    #         print('plshipper pass')
    #     else:
    #         print(sorted_recos)
    #         print('false')

    def _pl_shipper_info(self, correct, key='PLShipper'):
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]

            if correct:
                signal_line_index = sorted_recos[3].find('-')
                if sorted_recos[3][signal_line_index+1:].find('-') >= 0:
                    sorted_recos[3] = sorted_recos[3][:signal_line_index+1] + sorted_recos[3][signal_line_index+2:]

                signal_comma_index = sorted_recos[3].find(',')
                if sorted_recos[3][signal_comma_index+1] != ' ':
                    sorted_recos[3] = sorted_recos[3][:signal_comma_index+1] + ' ' + sorted_recos[3][signal_comma_index+1:]

                llc_index = sorted_recos[0].find('LLC')
                if sorted_recos[0][llc_index-1] != ' ':
                    sorted_recos[0] = sorted_recos[0][:llc_index] + ' ' + sorted_recos[0][llc_index:]

                ics_building_index = sorted_recos[3].find('ics Building')
                if sorted_recos[3].find('Logistics') < 0 and ics_building_index > 0:
                    sorted_recos[3] = sorted_recos[3][:ics_building_index-1] + 't' + sorted_recos[3][ics_building_index:]

                oad_index = sorted_recos[2].find('oad')
                if sorted_recos[2].find('Road') < 0 and oad_index > 0 :
                    sorted_recos[2] = sorted_recos[2][:oad_index-1] + 'R' + sorted_recos[2][oad_index:]

                e_ltd_index = sorted_recos[1].find('e Ltd')
                if sorted_recos[1].find('Asia Pte Ltd') < 0 and e_ltd_index > 0:
                    sorted_recos[1] = sorted_recos[1][:e_ltd_index - 1] + 't' + sorted_recos[1][e_ltd_index:]

            self._set_key_value_locations(key, sorted_recos, sorted_boxes)

    def _pl_consignee_info(self, key='PLConsignee'):
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]
            self._set_key_value_locations(key, sorted_recos, sorted_boxes)

    def _pl_page_info(self, key='PLPage'):
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes][0]
            self._set_key_value_locations(key, sorted_recos, sorted_boxes)

    def _pl_qty_uom_info(self, key = 'PLQtyUom'):
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes][0]
            self._set_key_value_locations(key, sorted_recos, sorted_boxes)

    def _pl_total_qty_info(self, rectify, key = 'PLTotalQty'):
        avg_length = 30
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]
            if len(sorted_recos) > 1:
                sorted_recos = sorted_recos[1][sorted_recos[1].find(' ')+1:]
                if rectify:
                    normal_length = sorted_boxes[0][1][0] - sorted_boxes[0][0][0]
                    normal_length = (normal_length + avg_length)//2
                    sorted_boxes[1][0][0] = sorted_boxes[1][1][0] - normal_length
                    sorted_boxes[1][3][0] = sorted_boxes[1][2][0] - normal_length
                sorted_boxes = sorted_boxes[1]
            else:
                sorted_recos = sorted_recos[0][sorted_recos[0].find('of ')+3:]
                if rectify:
                    sorted_boxes[0][0][0] = sorted_boxes[0][1][0] - avg_length
                    sorted_boxes[0][3][0] = sorted_boxes[0][2][0] - avg_length
            self._set_key_value_locations(key, sorted_recos, sorted_boxes)

    def _pl_nw_info(self, rectify, key = 'PLNW'):
        # 74            #    1
        # 76            #   .5
        # 86            #   13
        # 94.5          #  2.4
        # 99.5          #  160
        # 108           # 15.6
        # 47            #   KG
        avg_kg_length = 47
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]

            space_index = sorted_recos[0].find(' ')
            PLTotalNW = sorted_recos[0][:space_index]
            if PLTotalNW[0] == '.':
                num = float(PLTotalNW[1:])
                num /= 10
                PLTotalNW = str(num)
            PLTotalNW = str(float(PLTotalNW))
            PLWtUnit = sorted_recos[0][space_index+1:]
            TotalNW_boxes = sorted_boxes.copy()
            PLWtUnit_boxes = sorted_boxes.copy()

            if rectify:
                break_point = sorted_boxes[0][1][0] - avg_kg_length
                TotalNW_boxes[0][1][0] = break_point
                TotalNW_boxes[0][2][0] = break_point
                PLWtUnit_boxes[0][0][0] = break_point
                PLWtUnit_boxes[0][3][0] = break_point

            self._set_key_value_locations('PLTotalNW', PLTotalNW, TotalNW_boxes)
            self._set_key_value_locations('PLWtUnit', PLWtUnit, PLWtUnit_boxes)

    def _pl_no_info(self, rectify, key = 'PLNo'):
        # 103
        avg_no_length = 103
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]

            if len(sorted_recos) == 2:
                #print(sorted_boxes)
                sorted_recos = sorted_recos[1]
                sorted_boxes = sorted_boxes[1]

            else:
                sorted_recos = sorted_recos[0][sorted_recos[0].find('#:')+3:]
                if rectify:
                    breakpoint = sorted_boxes[0][1][0] - avg_no_length
                    sorted_boxes[0][0][0] = breakpoint
                    sorted_boxes[0][3][0] = breakpoint

            self._set_key_value_locations(key, sorted_recos, sorted_boxes)

    def _pl_commodity_qty_info(self, key = 'PLShipped'):
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]
            num_of_items = len(sorted_recos)

            self._add_commodity_list(num_of_items)
            self._set_key_value_locations_commodity_qty("PLCommodity.Qty", sorted_recos, sorted_boxes, num_of_items)

    def _pl_mpm_info(self, rectify, key = 'PLMPM'):
        avg_prefix_length = 218
        res_recos, res_boxes, index_in_boxes = self._get_sub_info_recos_by_key(key)
        index_in_boxes = np.array(list(itertools.chain.from_iterable(index_in_boxes[:])))
        if len(index_in_boxes) > 0:
            sorted_boxes = res_boxes[index_in_boxes]
            sorted_recos = res_recos[index_in_boxes]
            firstime = True
            item_index = 0
            while True:
                if firstime:
                    index = 0
                    index_before = 0
                else:
                    index = length_of_last
                    index_before = length_of_last

                circue_sorted_recos = sorted_recos[index:]
                for substr in circue_sorted_recos:
                    if substr.find('Country Of Origin') == 0:
                        country = [substr[19:]]
                        break
                    else:
                        index += 1

                if rectify:
                    sorted_boxes[index][0][0] += avg_prefix_length
                    sorted_boxes[index][3][0] += avg_prefix_length

                PLCommodity_PartNumber_reco = sorted_recos[index_before:index_before + 1]
                PLCommodity_PartNumber_box  = sorted_boxes[index_before:index_before + 1]
                PLCommodity_Desc_reco = sorted_recos[index_before + 1:index - 1]
                PLCommodity_Desc_box  = sorted_boxes[index_before + 1:index - 1]
                PLCommodity_COO_reco = country
                PLCommodity_COO_box  = sorted_boxes[index]

                self._set_key_value_locations_commodity_mpm(PLCommodity_PartNumber_reco, PLCommodity_PartNumber_box,
                                                            PLCommodity_Desc_reco, PLCommodity_Desc_box,
                                                            PLCommodity_COO_reco, PLCommodity_COO_box, item_index)

                if len(sorted_recos) > index + 3:
                    length_of_last = index + 3
                    item_index += 1
                    if firstime:
                        firstime = False
                else:
                    break

    def _add_commodity_list(self, num_of_items):
        tmp = {}
        self.final_result["PLCommodity"] = []
        while num_of_items != 0:
            self.final_result["PLCommodity"].append(deepcopy(tmp))
            num_of_items -= 1

    def _set_key_value_locations_commodity_qty(self, key, sorted_recos, sorted_boxes, num_of_items):
        for index_of_item in range(num_of_items):
            self.final_result["PLCommodity"][index_of_item][key] = {}
            self.final_result["PLCommodity"][index_of_item][key]["value"] = np.array(sorted_recos[index_of_item]).tolist()
            self.final_result["PLCommodity"][index_of_item][key]["locations"] = np.array(sorted_boxes[index_of_item]).tolist()

    def _set_key_value_locations_commodity_mpm(self, PartNumber_reco, PartNumber_box, Desc_reco, Desc_box, COO_reco, COO_box, item_index):
        self.final_result["PLCommodity"][item_index]["PLCommodity.PartNumber"] = {}
        self.final_result["PLCommodity"][item_index]["PLCommodity.PartNumber"]["value"] = np.array(PartNumber_reco).tolist()
        self.final_result["PLCommodity"][item_index]["PLCommodity.PartNumber"]["locations"] = np.array(PartNumber_box).tolist()

        self.final_result["PLCommodity"][item_index]["PLCommodity.Desc"] = {}
        self.final_result["PLCommodity"][item_index]["PLCommodity.Desc"]["value"] = np.array(Desc_reco).tolist()
        self.final_result["PLCommodity"][item_index]["PLCommodity.Desc"]["locations"] = np.array(Desc_box).tolist()

        self.final_result["PLCommodity"][item_index]["PLCommodity.COO"] = {}
        self.final_result["PLCommodity"][item_index]["PLCommodity.COO"]["value"] = np.array(COO_reco).tolist()
        self.final_result["PLCommodity"][item_index]["PLCommodity.COO"]["locations"] = np.array(COO_box).tolist()

    def pre_process(self):
        self._rectify_by_horizontal_line()
        self._enhance_image_by_gamma()

    def layout_extract(self):
        layout_config = self.read_config_json("./v_dar_sg_customs_pcg_packinglist_grpc/service/layout_config.json")
        thresholds_keys = self.read_config_json('./v_dar_sg_customs_pcg_packinglist_grpc/service/thresholds_keys.json')
        self._extract_info_by_key_position(layout_config, thresholds_keys)

    def key_info_extract(self, rectify = 1, correct = 1):
        self._pl_page_info()
        self._pl_shipper_info(correct)
        self._pl_no_info(rectify)
        self._pl_nw_info(rectify)
        self._pl_qty_uom_info()
        self._pl_total_qty_info(rectify)
        self._pl_consignee_info()

    def table_info_extract(self, rectify = 1):
        self._pl_commodity_qty_info()
        self._pl_mpm_info(rectify)
        if self.transform_matrix is not None:
            self._transform_boxes()

    def run(self, image, flip_bboxes, reco_result, image_type=None,
            rectify=False, correct=False, show=False, save_to_folder=False):
        self._reset_()
        self.__prepare__(image, flip_bboxes, reco_result, image_type=image_type)
        self.pre_process()
        self.layout_extract()
        self.key_info_extract(rectify, correct)
        self.table_info_extract(rectify)
        return_json = self.check_json()
        return return_json
