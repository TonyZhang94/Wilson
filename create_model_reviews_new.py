"""
这是我写的第一个pandas,见谅见谅...json有点恶心。
"""

import datetime
import json
import re

import pandas as pd
import numpy as np
import psycopg2
import scipy.stats
import math
# import matplotlib.pyplot as plt

from analysis.script.utils import *
from zhuican.test import logger, cls_logger, log
from analysis.script.calculate_confidence import Confidence

'''

                            _ooOoo_
                           o8888888o
                           88" . "88
                           (| -_- |)
                            O\ = /O
                        ____/`---'\____
                      .   ' \\| |// `.
                       / \\||| : |||// \`
                     / _||||| -:- |||||- \
                       | | \\\ - /// | |
                     | \_| ''\---/'' | |
                      \ .-\__ `-` ___/-. /
                   ___`. .' /--.--\ `. . __
                ."" '< `.___\_<|>_/___.' >'"".
               | | : `- \`.;`\ _ /`;.`/ - ` : | |
                 \ \ `-. \_ __\ /__ _/ .-` / /
         ======`-.____`-.___\_____/___.-`____.-'======
                            `=---='

         .............................................
                  佛祖保佑             永无BUG
          佛曰:
                  写字楼里写字间，写字间里程序员；
                  程序人员写程序，又拿程序换酒钱。
                  酒醒只在网上坐，酒醉还来网下眠；
                  酒醉酒醒日复日，网上网下年复年。
                  但愿老死电脑间，不愿鞠躬老板前；
                  奔驰宝马贵者趣，公交自行程序员。
                  别人笑我忒疯癫，我笑自己命太贱；
                  不见满街漂亮妹，哪个归得程序员？

'''


@cls_logger
class CreateModelReviews:
    # 初始化
    def __init__(self, pcid, cid):
        self.pcid = pcid
        self.cid = cid
        self.engine_dg = get_99_engine('report_dg')
        self.dg = 'report_dg'
        self.engine_face = get_99_engine('fact_library')
        # self.engine_tencent = get_tencent_engine('crawl_mmb_category')
        self.standard_library = get_99_engine('standard_library')
        self.basics = get_99_engine('basics')
        self.engine_web = get_99_engine('zhuican_web')
        self.df = self.get_model()
        self.reviews_tab = 'product_brain.product_brain_pcid{}'.format(self.pcid)
        self.values_list = self.df.columns.values.tolist()
        self.generic_word = ['电器', '质量保证', '搅拌机', '产品质量', '货品', '满意度', '器具', '服务质量', '功能', '高质量', '效果', '物流', '快递业',
                             '外观']
        self.pic_seq = 1

    def get_model(self):
        sql = "select * from report_model.model_report_pcid{}cid{}".format(self.pcid, self.cid)
        return pd.read_sql_query(sql, self.engine_dg)

    # log.logger.info('函数开始运行')
    # 获取sku属性
    @logger
    def get_sku(self):
        sku_data = {}
        data = {}
        self.df['sku'] = ''
        for values in self.values_list:
            if values in ['model', 'brand', 'title']:
                continue
            sql = (
                "SELECT * FROM sku_zh_en.sku_translation WHERE sku_en = '{}'".format(values)
            )
            df = pd.read_sql_query(sql, get_99_engine("standard_library"))
            if df.empty:
                continue
            sku_data[df['sku_zh'].values[0]] = df['sku_en'].values[0]
        for k, v in self.df.iterrows():
            for i, j in sku_data.items():
                if v[j] != '' and v[j] is not None:
                    data[i] = v[j]
            self.df.at[k, 'sku'] = json.dumps(data, ensure_ascii=False)
        self.df.rename(columns={
            'total_sold_price_month_increase': 'total_sold_price_increment',
            'biz30day_month_increase': 'biz30day_increment',
            'rate_season_biz30day': 'season_biz30day_raise',
            'rate_season_total_sold_price': 'season_total_sold_price_raise',
            'aver_price': 'price',
        }, inplace=True)

    # 获取ｓｕｂｍａｒｋｅｔ列
    @logger
    def get_submarket(self):
        sql = (
            "select distinct brand, model, sm_id, submarket"
            " from fact_model_submarket.pcid{} where cid = {} and sm_id not like 'p%%'"
        ).format(self.pcid, self.cid)
        self.df_sub = pd.read_sql_query(sql, self.engine_face)

        def coult(df):
            tmp = {}
            for k, v in df.iterrows():
                tmp[str(v['sm_id'])] = (v['submarket'])
            return json.dumps(tmp, ensure_ascii=False)

        df1 = self.df_sub.groupby(['model', 'brand']).apply(coult).reset_index()

        df1.columns = ['model', 'brand', 'submarket']
        self.df = pd.merge(self.df, df1, 'inner', on=['model', 'brand'])

    # 计算销量销售额的年增长率月增长率季度增长率和月度增量
    def compute_brand_submarket(self, df):
        df['season_biz30day'] = df['biz30day'].rolling(window=pd.to_timedelta('90 days')).sum()
        df['season_total_sold_price'] = df['total_sold_price'].rolling(
            window=pd.to_timedelta('90 days')).sum()

        df['biz30day_increment'] = df['biz30day'] - df.shift(freq='MS')['biz30day']
        df['total_sold_price_increment'] = df['total_sold_price'] - df.shift(freq='MS')['total_sold_price']
        df['rate_ring_biz30day'] = df['biz30day'].pct_change(freq='MS') * 100
        df['rate_ring_total_sold_price'] = df['total_sold_price'].pct_change(freq='MS') * 100

        df['season_biz30day_raise'] = df['season_biz30day'].pct_change(periods=3, freq='MS') * 100
        df['season_total_sold_price_raise'] = df['season_total_sold_price'].pct_change(
            periods=3, freq='MS') * 100

        df['rate_year_biz30day'] = df['biz30day'].pct_change(periods=12, freq='MS') * 100
        df['rate_year_total_sold_price'] = df['total_sold_price'].pct_change(periods=12, freq='MS') * 100

        return df

    # 根据model brand计算各种增长率，计算函数在上方
    @logger
    def get_compute(self):
        self.df['price'] = self.df.total_sold_price // self.df.biz30day
        self.df.columns = self.df.columns.str.strip()

        self.df.drop(columns=[
            'rate_ring_biz30day', 'rate_ring_total_sold_price', 'season_biz30day_raise',
            'season_total_sold_price_raise', 'rate_year_biz30day', 'rate_year_total_sold_price',
            'biz30day_increment', 'total_sold_price_increment',
        ], inplace=True)

        # self.df = create_datamonth_index(self.df)
        group_by = ['brand', 'model']
        self.df.drop_duplicates(['brand', 'model', 'datamonth'], inplace=True)
        self.df['datamonth'] = translate_seriels_to_datetime(self.df['datamonth'])
        self.df = optimize_df_memory_usage(self.df, category_columns=['brand', 'model'])
        # self.df.sort_values(group_by + ['datamonth'], inplace=True)
        # self.df = self.df.groupby(group_by).apply(self.compute_brand_submarket).reset_index(drop=True)
        self.df = compute_all(
            self.df, group_by,
            rolling_sum_data=[
                [TIME_INTERVAL_SEASON, {
                    'biz30day': 'season_biz30day',
                    'total_sold_price': 'season_total_sold_price',
                }],
            ],
            pct_change_data=[
                [1, 'MS', {
                    'biz30day': 'rate_ring_biz30day',
                    'total_sold_price': 'rate_ring_total_sold_price',
                }],
                [3, 'MS', {
                    'season_biz30day': 'season_biz30day_raise',
                    'season_total_sold_price': 'season_total_sold_price_raise',
                }],
                [12, 'MS', {
                    'biz30day': 'rate_year_biz30day',
                    'total_sold_price': 'rate_year_total_sold_price',
                }],
            ],
            diff_data=[
                [1, 'MS', {
                    'biz30day': 'biz30day_increment',
                    'total_sold_price': 'total_sold_price_increment',
                }],
            ],
        )

        self.df['datamonth'] = self.df['datamonth'].map(lambda x: x.strftime(DATAMONTH_FORMAT))

    def json(self):
        self.df_com['top_target'] = self.df_com['top_target'].str.replace('\'"', '"')
        self.df_com['top_target'] = self.df_com['top_target'].str.replace('"\'', '"')
        self.df_com['top_target'] = self.df_com['top_target'].str.replace('\'', '')
        self.df_com['top_target'] = self.df_com['top_target'].str.replace('\\', '')

        self.df_com['model_target_rank'] = self.df_com['model_target_rank'].str.replace('\'"', '"')
        self.df_com['model_target_rank'] = self.df_com['model_target_rank'].str.replace('"\'', '"')
        self.df_com['model_target_rank'] = self.df_com['model_target_rank'].str.replace('\'', '')
        self.df_com['model_target_rank'] = self.df_com['model_target_rank'].str.replace('\\', '')

        self.df_com['aver_model_target_ratings'] = self.df_com['aver_model_target_ratings'].str.replace('\'"', '"')
        self.df_com['aver_model_target_ratings'] = self.df_com['aver_model_target_ratings'].str.replace('"\'', '"')
        self.df_com['aver_model_target_ratings'] = self.df_com['aver_model_target_ratings'].str.replace('\'', '')
        self.df_com['aver_model_target_ratings'] = self.df_com['aver_model_target_ratings'].str.replace('\\', '')

        self.df_com['model_target_ratings'] = self.df_com['model_target_ratings'].str.replace('\'"', '"')
        self.df_com['model_target_ratings'] = self.df_com['model_target_ratings'].str.replace('"\'', '"')
        self.df_com['model_target_ratings'] = self.df_com['model_target_ratings'].str.replace('\'', '')
        self.df_com['model_target_ratings'] = self.df_com['model_target_ratings'].str.replace('\\', '')

        self.df_com['target_score'] = self.df_com['target_score'].str.replace('\'"', '"')
        self.df_com['target_score'] = self.df_com['target_score'].str.replace('"\'', '"')
        self.df_com['target_score'] = self.df_com['target_score'].str.replace('\'', '')
        self.df_com['target_score'] = self.df_com['target_score'].str.replace('\\', '')

    def fuzzy_set_theory(self, df_com_copy, tag_list):
        origin = df_com_copy.copy()
        bad_list = origin['grade'] == -1
        origin.loc[bad_list, ['frequency']] = -origin.loc[bad_list, ['frequency']]

        def fun_cnt_frequence_model_brand(df):
            cnt = 0
            pos_part = df[df["grade"] == 1]
            for k, v in pos_part.iterrows():
                cnt = cnt + v["frequency"]
            df["cnt_freq_model_brand_pos"] = cnt

            cnt = 0
            neg_part = df[df["grade"] == -1]
            for k, v in neg_part.iterrows():
                cnt = cnt + v["frequency"]
            df["cnt_freq_model_brand_neg"] = -cnt

            cnt = 0
            neu_part = df[df["grade"] == 0]
            for k, v in neu_part.iterrows():
                cnt = cnt + v["frequency"]
            df["cnt_freq_model_brand_neu"] = cnt

            return df

        data_step_1 = origin.copy()
        data_step_1["cnt_freq_model_brand_pos"] = 0
        data_step_1["cnt_freq_model_brand_neg"] = 0
        data_step_1["cnt_freq_model_brand_neu"] = 0
        data_step_1 = origin.groupby(['model', 'brand', "tag"]).apply(fun_cnt_frequence_model_brand)
        data_step_1['cnt_freq_model_brand_pos'] = data_step_1['cnt_freq_model_brand_pos'].fillna(0)
        data_step_1['cnt_freq_model_brand_neg'] = data_step_1['cnt_freq_model_brand_neg'].fillna(0)
        data_step_1['cnt_freq_model_brand_neu'] = data_step_1['cnt_freq_model_brand_neu'].fillna(0)
        data_step_1_drop_duplicates = data_step_1.drop_duplicates(['model', 'brand', "tag"])

        def membership_function(df):
            pos = df["cnt_freq_model_brand_pos"].values[0]
            neg = df["cnt_freq_model_brand_neg"].values[0]
            neu = df["cnt_freq_model_brand_neu"].values[0]
            denominator = pos + neg + neu
            if 0 != denominator:
                mem_func = 1 / denominator
                df["mem_degree_pos"] = df["cnt_freq_model_brand_pos"] * mem_func
                df["mem_degree_neg"] = df["cnt_freq_model_brand_neg"] * mem_func
                df["mem_func_inverse"] = denominator
            else:
                df["mem_degree_pos"] = 0
                df["mem_degree_neg"] = 0
                df["mem_func_inverse"] = 0
            return df

        data_step_2 = data_step_1_drop_duplicates.groupby(['model', 'brand', "tag"]).apply(membership_function)
        data_step_2 = data_step_2.reset_index(drop=True)

        aspects_num = 5
        weight = 1 / aspects_num
        weights = dict()
        for tag in tag_list:
            weights[tag] = weight

        def IFWA(df):
            log.logger.info("==========Fussy Num of Product==========")
            ret = [1, 1]
            has_tags = df["tag"].values
            for tag in tag_list:
                if tag not in has_tags:
                    continue
                ret[0] *= (1 - df[df["tag"] == tag]["mem_degree_pos"].values[0]) ** weights[tag]
                ret[1] *= df[df["tag"] == tag]["mem_degree_neg"].values[0] ** weights[tag]
            df["IFWA_0"] = 1 - ret[0]
            df["IFWA_1"] = ret[1]
            return df

        data_step_3 = data_step_2.groupby(['model', 'brand']).apply(IFWA)
        products = data_step_3.drop_duplicates(["model", "brand"]).reset_index()
        products_num = len(products)

        def dominance_degree(product1, product2):
            if product1[0] != product2[0]:
                return round((product1[0] - product2[0]) \
                             / ((product1[0] - product2[0]) + max((product1[1] - product2[1]), 0)), 4)
            else:
                if product1[1] < product2[1]:
                    return 1
                else:
                    return 0

        def dominance_degree_row(self_model, self_brand, self_IFWA):
            row = list()
            for k, v in products.iterrows():
                model, brand, IFWA = v["model"], v["brand"], [v["IFWA_0"], v["IFWA_1"]]
                if self_model != model and self_brand != brand:
                    if self_IFWA[0] >= IFWA[0]:
                        row.append(dominance_degree(product1=self_IFWA, product2=IFWA))
                    else:
                        row.append(1 - dominance_degree(product1=IFWA, product2=self_IFWA))
                else:
                    row.append(0)
            return row

        dominance_degree_matrix = []
        for k, v in products.iterrows():
            self_model, self_brand, self_IFWA = v["model"], v["brand"], [v["IFWA_0"], v["IFWA_1"]]
            dominance_degree_matrix.append(
                dominance_degree_row(self_model=self_model, self_brand=self_brand, self_IFWA=self_IFWA))

        def cal_quota(df):
            rank = df.index[0]
            df["fi_plus"] = sum(dominance_degree_matrix[rank])
            for row in dominance_degree_matrix:
                df["fi_minus"] += row[rank]
            df["fi"] = df["fi_plus"] - df["fi_minus"]
            return df

        products["fi_plus"], products["fi_minus"], products["fi"] = 0, 0, 0
        products_fi = products.groupby(["model", "brand"]).apply(cal_quota)

        return products_fi

        # 获取评论

    @logger
    def get_comment(self):
        """
         read data，select data，adjust frequency
        """
        sql = (
            "SELECT itemid, frequency, grade, target, opinion, tag, brand, model"
            " FROM comment.review_analysis_pcid{}_cid{}"
        ).format(self.pcid, self.cid)
        # sql = ("SELECT itemid, frequency, grade, target, opinion, tag, brand, model "
        #        "FROM comment.review_analysis_pcid{}_cid{}_1;".format(self.pcid, self.cid))

        start = NOW()
        df_comment = pd.read_sql_query(sql, self.engine_dg)
        df_comment = pd.merge(
            df_comment, self.df[['brand', 'model']].drop_duplicates(), how='inner', on=['brand', 'model'])
        # df_comment.to_csv("tmp_comment.csv")
        # df_comment = pd.read_csv("tmp_comment.csv", index_col=0)
        log.logger.info('评论数据读出 {}s'.format((NOW() - start).total_seconds()))
        self.df_com = pd.DataFrame()

        tag_list = ['质量', '款式', '功能', '服务']
        for k in tag_list:
            row_index = df_comment[df_comment['tag'] == k]
            if self.df_com.empty:
                self.df_com = row_index
            else:
                self.df_com = pd.concat([self.df_com, row_index])
        self.df_com = self.df_com.fillna(0)
        df_com_copy = self.df_com.copy()

        bad_list = df_com_copy['grade'] == -1
        df_com_copy.loc[bad_list, ['frequency']] = -df_com_copy.loc[bad_list, ['frequency']]
        zhong_list = df_com_copy['grade'] == 0
        df_com_copy.loc[zhong_list, ['frequency']] = 0

        """
        add up frequency
        """
        # model的频次
        df = df_com_copy.groupby(['brand', 'model'])['frequency'].sum().reset_index()
        df.rename(columns={"frequency": "model_score"}, inplace=True)
        self.df_com = pd.merge(self.df_com, df, 'left', on=['model', 'brand'])

        # tag的频次
        df = df_com_copy.groupby(['brand', 'model', 'tag'])['frequency'].sum().reset_index()
        df.rename(columns={"frequency": "tag_score"}, inplace=True)
        self.df_com = pd.merge(self.df_com, df, 'left', on=['model', 'brand', 'tag'])

        # target的频次
        df = df_com_copy.groupby(['brand', 'model', 'tag', 'target'])['frequency'].sum().reset_index()
        df.rename(columns={"frequency": "target_score"}, inplace=True)
        self.df_com = pd.merge(self.df_com, df, 'left', on=['model', 'brand', 'tag', 'target'])

        """
        add up tag，target zong and find min
        """
        # 计算tag，target_zong
        def cal_zong(df, score, zong_score):
            min = df[score].min()
            if min > 0:
                df[zong_score] = df[score].max()
            else:
                df[zong_score] = df[score].max() - df[score].min()
            return df

        df_com = self.df_com.groupby(['tag']).apply(cal_zong, score='tag_score', zong_score='tag_zong')
        df_com = df_com.groupby(['tag', 'target']).apply(cal_zong, score='target_score', zong_score='target_zong')

        # 计算tag，target最小值
        def cal_min(df, score, min):
            min1 = df[score].min()
            df[min] = min1
            return df

        df_com = df_com.groupby(['tag']).apply(cal_min, score='tag_score', min='tag_min')
        df_com = df_com.groupby(['tag', 'target']).apply(cal_min, score='target_score', min='target_min')

        """
        cal ratings
        """
        # target 打分
        df_com_bak = df_com.drop_duplicates(["model", "brand", "tag", "target"])[[
            "model", "brand", "tag", "target", "target_score"]]

        # # 计算tag-target总值
        def cal_sum(df):
            df["target_sum"] = df["target_score"].sum()
            return df
        df_com_bak = df_com_bak.groupby(['tag', 'target']).apply(cal_sum).sort_values([
            "target_score", "brand", "model"], ascending=False)
        df_com_bak["target_sum"] = df_com_bak["target_sum"].astype("int")

        # # 计算target基本信息
        # # 不分tag计算？
        tag_target_info = df_com_bak.drop_duplicates(["tag", "target"])[[
            "tag", "target", "target_sum"]].sort_values('target_sum', ascending=False)
        base_info = dict()
        serial = {key: -1 for key in tag_list}
        prev = {key: -99999 for key in tag_list}
        max_blanks = dict()
        for k, v in tag_target_info.iterrows():
            key = "%s-%s" % (v["tag"], v["target"])
            if v["target_sum"] != prev[v["tag"]]:
                serial[v["tag"]] += 1
                prev[v["tag"]] = v["target_sum"]
            base_info[key] = str(serial[v["tag"]]) + " " + str(v["target_sum"])

        # # 具体打分
        mu, sigma = 0, 1

        zero_node = 1
        small_node = 10
        normal_node = 1000000  # 10 ^ 6

        def target_rating(df):
            tag, target = df["tag"].values[0], df["target"].values[0]
            side = serial[tag]
            try:
                info = base_info["%s-%s" % (tag, target)]
                serial_no, target_sum = info.split(" ")
                avg = 75 - int(serial_no) / side / 0.02
            except ZeroDivisionError:
                avg = 50
                target_sum = 0

            base = 5
            mul = 10
            special = 10

            diff = len(df)
            if diff <= zero_node or int(target_sum) <= 0:
                if int(target_sum) < special:
                    df["model_target_ratings"] = 0
                else:
                    for k, v in df.iterrows():
                        score = (v["target_score"] - special) * 6.66 + 50
                        df.at[k, "model_target_ratings"] = round(min(100, score), 2)
                return df, None, None
                # x = df["model_target_ratings"].values
                # msg = "size {} max {} min {} avg {} sigma={} sum {}".format(
                #     diff, max(x), min(x), round(sum(x)/len(x), 2), sigma, target_sum)
                # return df, x, "tag %s pos %.2f %s " % (tag, round(avg, 2), target)+msg

            if diff < normal_node:
                size = normal_node
                step = size / (diff + 1)
            else:
                size = diff + 1
                step = 1
            block = 1 / size

            bottom = (scipy.stats.norm.ppf(block * 1 * step, mu, sigma) + base) * mul
            top = (scipy.stats.norm.ppf(block * diff * step, mu, sigma) + base) * mul
            blank = 100 - top

            #  10^6 数量级的model没有问
            # 10^6 * 5 ~ 10^7 数量级的model会有个位数边缘越界情况，处理边缘上越界
            if bottom < 0 or top > 100:
                print("adjust size =", diff)
                mul = 100 / (top - bottom)

            try:
                max_blank = max_blanks[tag]
            except KeyError:
                max_blank = 100 - (scipy.stats.norm.ppf(block*(size-size/(1+side)), mu, sigma) + base) * mul
                max_blanks[tag] = max_blank
            rectify = (0.04 * avg - 2) * max_blank

            if zero_node < diff <= small_node:
                dis, rank = round(100 / (diff + 5), 2), diff + 1
                for k, v in df.iterrows():
                    rank -= 1
                    df.at[k, "model_target_ratings"] = round(min(max(dis*rank+0.1*rectify, 0), 100), 2)
            elif small_node < diff:
                rank = diff + 1
                for k, v in df.iterrows():
                    rank -= 1

                    co = rank / diff
                    share = 0.01 * avg - 0.5
                    if share > 0:
                        offset = -((2 - 2 * co) ** 2) * share * blank
                    elif share < 0:
                        offset = -((2 * co) ** 2) * share * blank
                    else:
                        offset = 0
                    fx = rank * step * block
                    ppf = scipy.stats.norm.ppf(fx, mu, sigma)
                    # 10^6 * 5 ~ 10^7 数量级的model，处理边缘下越界
                    ppf = round((ppf + base) * mul + offset, 2)
                    df.at[k, "model_target_ratings"] = round(min(max(ppf+rectify, 0), 100), 2)
            else:
                print("error condition")

            return df, None, None

        def target_rating_func(df):
            df, x, msg = target_rating(df)
            return df

        # df_com_bak = df_com_bak.sort_values(["target_score", "brand", "model"], ascending=True)
        df_com_bak = df_com_bak.groupby(["tag", "target"]).apply(target_rating_func)
        del df_com_bak["target_score"], df_com_bak["target_sum"]
        df_com = pd.merge(df_com, df_com_bak, "left", on=["model", "brand", "tag", "target"])

        # tag 打分
        # # 计算tag的得分
        df_com_bak = df_com.drop_duplicates(["model", "brand", "tag", "target"])[[
            "model", "brand", "tag", "target", "target_score", "model_target_ratings", "target_min"]].sort_values([
            "brand", "model", "model_target_ratings"], ascending=False)

        def tag_ratings_func(df):
            target_min = min(min(df["target_min"].values), 0)
            total = 0
            add = {k: 0 for k in tag_list}
            cnt = {k: 0 for k in tag_list}
            threshold = len([x for x in df["model_target_ratings"].values if x > 0]) * 0.6
            for k, v in df.iterrows():
                if 0 != v["model_target_ratings"]:
                    if cnt[v["tag"]] >= threshold:
                        continue
                    total = total + v["target_score"] - target_min
                    # total = total + v["target_score"]
                    add[v["tag"]] += (v["target_score"] - target_min) * v["model_target_ratings"]
                    # add[v["tag"]] += (v["target_score"]) * v["model_target_ratings"]
                    cnt[v["tag"]] += 1
            for tag in tag_list:
                pos = df["tag"] == tag
                # total = total + threshold - cnt[tag]
                if total != 0 and add[tag] / total > 100:
                    print(df)
                    print(tag, total, add[tag], target_min, cnt[tag])
                if 0 != total:
                    df.loc[pos, "model_tag_ratings"] = max(round(add[tag] / total, 2), 0)
                else:
                    df.loc[pos, "model_tag_ratings"] = total
            return df

        df_com_bak = df_com_bak.groupby(["model", "brand", "tag"]).apply(tag_ratings_func)
        del df_com_bak["target_score"], df_com_bak["model_target_ratings"], df_com_bak["target_min"]
        df_com = pd.merge(df_com, df_com_bak, "left", on=["model", "brand", "tag", "target"])

        # model 打分
        df_com_bak = df_com.drop_duplicates(["brand", "model", "tag"])[[
            "model", "brand", "tag", "tag_score", "model_tag_ratings", "tag_min"]]

        def model_ratings_func(df):
            tag_min = min(min(df["tag_min"].values), 0)
            total, score = 0, 0
            for k, v in df.iterrows():
                if 0 != v["model_tag_ratings"]:
                    total = total + v["tag_score"] - tag_min
                    # total = total + v["tag_score"]
                    score += (v["tag_score"] - tag_min) * v["model_tag_ratings"]
                    # score += (v["tag_score"]) * v["model_tag_ratings"]
            if total != 0:
                df["model_ratings"] = max(round(score / total, 2), 0)
                # df["model_ratings"] = max(round(score / 4, 2), 0)
            else:
                df["model_ratings"] = total
                # df["model_ratings"] = 4
            return df

        df_com_bak = df_com_bak.groupby(["brand", "model"]).apply(model_ratings_func)
        del df_com_bak["tag_score"], df_com_bak["model_tag_ratings"], df_com_bak["tag_min"]
        df_com = pd.merge(df_com, df_com_bak, "left", on=["model", "brand", "tag"])

        # 合并df_com到self.df_com
        df_com = df_com[['model', 'brand', 'tag', 'target', 'model_ratings', 'model_tag_ratings', 'model_target_ratings']]
        self.df_com = pd.merge(self.df_com, df_com, 'left', on=['model', 'brand', 'tag', 'target']).drop_duplicates()

        """
        average ratings of model，tag，target
        merge to self.df_com
        """
        # model平均得分
        df_aver = self.df_com.drop_duplicates(['model', 'brand'])
        self.df_com['aver_model_ratings'] = round(df_aver['model_ratings'].sum() / len(df_aver), 2)

        # tag平均得分
        def aver_tag(df):
            aver_model_tag_ratings = round(df['model_tag_ratings'].sum() / len(df), 2)
            return aver_model_tag_ratings

        df = self.df_com.drop_duplicates(['model', 'brand', 'tag']).groupby(['tag']).apply(aver_tag).reset_index()
        df.columns = ['tag', 'aver_model_tag_ratings']
        df = df.fillna(0)
        self.df_com = pd.merge(self.df_com, df, 'left', on=['tag'])

        # target平均得分
        def aver_target(df):
            aver_model_tag_ratings = round(df['model_target_ratings'].sum() / len(df), 2)
            return aver_model_tag_ratings

        df = self.df_com.drop_duplicates(['model', 'brand', 'tag', 'target']).groupby(['target']).apply(
            aver_target).reset_index()
        df.columns = ['target', 'aver_model_target_ratings']
        df = df.fillna(0)
        self.df_com = pd.merge(self.df_com, df, 'left', on=['target'])

        """
        top ratings of model，tag，target
        merge to self.df_com
        """
        self.df_com = self.df_com.fillna(0)
        top_rating = self.df_com.copy()

        # model的最高分
        top_model = top_rating.sort_values('model_ratings', ascending=False)['model_ratings'].values[0]
        top_rating['top_model'] = top_model

        # tag的最高分
        def top_tag(df):
            top_tag = df.sort_values('model_tag_ratings', ascending=False)['model_tag_ratings'].values[0]
            df['top_tag'] = top_tag
            return df

        top_rating = top_rating.groupby(['tag']).apply(top_tag)

        # target的最高分
        def top_target(df):
            top_target = df.sort_values('model_target_ratings', ascending=False)['model_target_ratings'].values[0]
            df['top_target'] = top_target
            return df

        top_rating = top_rating.groupby(['tag', 'target']).apply(top_target)

        # top_tag键值化
        def com(df):
            list1 = {}
            for k, v in df.iterrows():
                list1[v['tag']] = v['top_tag']
            df['top_tag'] = json.dumps(list1, ensure_ascii=False)
            return df

        top_rating = top_rating.groupby(['model', 'brand']).apply(com)

        # top_target键值化
        def top(df):
            list1 = {}
            for k, v in df.iterrows():
                if v['target'] in self.generic_word:
                    continue
                list1[v['target']] = v['top_target']
            df['top_target'] = json.dumps(list1, ensure_ascii=False)
            df = df.drop_duplicates(['model', 'brand', 'tag'])
            return df

        top_rating = top_rating.groupby(['model', 'brand', 'tag']).apply(top)

        top_rating = top_rating.reindex(
            columns=['brand', 'model', 'tag', 'top_model', 'top_tag', 'top_target'
                     ])
        self.df_com = pd.merge(self.df_com, top_rating, 'left', on=['model', 'brand', 'tag']).drop_duplicates()

        """
        rank model，tag，target by ratings
        merge to self.df_com
        """
        # 计算model得分排名
        def rank(df, ratings, columns):
            num = 0
            prev = -999
            df = df.sort_values([str(ratings)], ascending=False)
            for k, v in df.iterrows():
                if prev != v[ratings]:
                    num += 1
                    prev = v[ratings]
                df.at[k, columns] = num
            return df

        df_rank = self.df_com.drop_duplicates(['model', 'brand'])[['model', 'brand', 'model_ratings']]
        df_rank['model_rank'] = ''
        df_rank = rank(df_rank, 'model_ratings', 'model_rank')
        del df_rank['model_ratings']
        df_rank = df_rank.fillna(0)
        self.df_com = pd.merge(self.df_com, df_rank, 'left', on=['model', 'brand'])

        # 计算tag得分排名
        df_rank = self.df_com.drop_duplicates(['model', 'brand', 'tag'])[['model', 'brand', 'tag', 'model_tag_ratings']]
        df_rank = df_rank.fillna(0)

        def rank(df, ratings, columns):
            num = 0
            prev = -999
            df = df.sort_values([str(ratings)], ascending=False)
            max = len(set(df[ratings].values))
            for k, v in df.iterrows():
                if prev != v[ratings]:
                    num += 1
                    prev = v[ratings]
                df.at[k, columns] = str(num) + '/' + str(max)
            return df

        df_rank = df_rank.groupby(['tag']).apply(rank, ratings='model_tag_ratings', columns='model_tag_rank')
        df_rank = df_rank[['model', 'brand', 'tag', 'model_tag_rank']]
        self.df_com = pd.merge(self.df_com, df_rank, 'left', on=['model', 'brand', 'tag'])

        # 计算target得分排名
        def rank(df, ratings, columns):
            num = 0
            prev = -999
            df = df.sort_values([str(ratings)], ascending=False)
            max = len(set(df[ratings].values))
            for k, v in df.iterrows():
                if v['target'] in self.generic_word:
                    continue
                if prev != v[ratings]:
                    num += 1
                    prev = v[ratings]
                df.at[k, columns] = str(num) + '/' + str(max)
            return df

        df_rank = self.df_com.drop_duplicates(['model', 'brand', 'tag', 'target'])
        df_rank = df_rank.groupby(['target']).apply(rank, ratings='model_target_ratings', columns='model_target_rank')
        df_rank = df_rank[['model', 'brand', 'model_target_rank', 'target']]
        self.df_com = pd.merge(self.df_com, df_rank, 'left', on=['model', 'brand', 'target'])
        self.df_com['model_target_rank'] = self.df_com['model_target_rank'].fillna(0)

        """
        json格式的转换
        """
        def com(df):
            list1 = {}
            list2 = {}
            list3 = {}

            for k, v in df.iterrows():
                if v['target'] in self.generic_word:
                    continue
                list1[v['target']] = v['model_target_rank']
                list2[v['target']] = v['model_target_ratings']
                list3[v['target']] = v['aver_model_target_ratings']
            df['model_target_ratings'] = json.dumps(list2, ensure_ascii=False)
            df['model_target_rank'] = json.dumps(list1, ensure_ascii=False)
            df['aver_model_target_ratings'] = json.dumps(list3, ensure_ascii=False)
            return df

        self.df_com['model_tag_ratings'] = self.df_com['model_tag_ratings'].astype(str)
        self.df_com['model_tag_rank'] = self.df_com['model_tag_rank'].astype(str)
        self.df_com['aver_model_tag_ratings'] = self.df_com['aver_model_tag_ratings'].astype(str)

        def tag_ratings(df):
            frequency = {}
            tag_rank = {}
            aver_model_tag_ratings = {}
            for k, v in df.iterrows():
                frequency[v['tag']] = float(v['model_tag_ratings'])
                tag_rank[v['tag']] = v['model_tag_rank']
                aver_model_tag_ratings[v['tag']] = float(v['aver_model_tag_ratings'])
            df['model_tag_ratings'] = json.dumps(frequency, ensure_ascii=False)
            df['model_tag_rank'] = json.dumps(tag_rank, ensure_ascii=False)
            df['aver_model_tag_ratings'] = json.dumps(aver_model_tag_ratings, ensure_ascii=False)
            df = df.drop_duplicates()
            return df

        self.df_com = self.df_com.groupby(['model', 'brand']).apply(tag_ratings).reset_index()
        self.df_com['model_target_rank'] = self.df_com['model_target_rank'].fillna(0)
        self.df_com = (self.df_com.groupby(['model', 'brand', 'tag']).apply(com).reset_index()).drop_duplicates()
        self.df_com['tag_score'] = self.df_com['tag_score'].astype(str)

        def tag_score(df):
            tag_score = {}
            for k, v in df.iterrows():
                tag_score[v['tag']] = float(v['tag_score'])
            df['tag_score'] = json.dumps(tag_score, ensure_ascii=False)
            return df

        self.df_com = self.df_com.groupby(['model', 'brand']).apply(tag_score)

        # target 的频次
        def com(df):
            list1 = {}
            for k, v in df.iterrows():
                if v['target'] in self.generic_word:
                    continue
                list1[v['target']] = v['target_score']
            df['target_score'] = json.dumps(list1, ensure_ascii=False)
            df = df.drop_duplicates(['model', 'brand', 'tag'])
            return df

        df = (self.df_com.groupby(['model', 'brand', 'tag']).apply(com))
        df = df.reindex(columns=['model', 'brand', 'tag', 'target_score']).reset_index(drop=True)
        del self.df_com['target_score']
        self.df_com = pd.merge(self.df_com, df, 'left', on=['model', 'brand', 'tag']).drop_duplicates()

        def func(df):
            top_target = {}
            model_target_rank = {}
            aver_model_target_ratings = {}
            model_target_ratings = {}
            target_score = {}
            for k, v in df.iterrows():
                top_target['\"%s\"' % v['tag']] = v['top_target']
                model_target_rank['\"%s\"' % v['tag']] = v['model_target_rank']
                aver_model_target_ratings['\"%s\"' % v['tag']] = v['aver_model_target_ratings']
                model_target_ratings['\"%s\"' % v['tag']] = v['model_target_ratings']
                target_score['\"%s\"' % v['tag']] = v['target_score']
            df['top_target'] = str(top_target)
            df['model_target_rank'] = str(model_target_rank)
            df['aver_model_target_ratings'] = str(aver_model_target_ratings)
            df['model_target_ratings'] = str(model_target_ratings)
            df['target_score'] = str(target_score)
            df = df.drop_duplicates()
            return df

        self.df_com = self.df_com.drop_duplicates(['model', 'brand', 'tag'])
        self.df_com = self.df_com.groupby(['model', 'brand']).apply(func)
        # self.df_com['top_target'] = self.df_com['top_target'].str.replace(r"'\'",'')
        # 格式化json
        self.json()

        self.df = pd.merge(self.df, self.df_com, 'left', on=['brand', 'model'])
        # self.df = self.df.drop_duplicates(['model','brand','datamonth','model_tag_ratings','model_target_ratings','tag_ratings','target_score'])
        self.df = self.df.drop_duplicates(
            ['model', 'brand', 'datamonth', 'model_tag_ratings', 'model_target_ratings', 'tag_score', 'target_score'])

    # 格式化数据并且存到数据库里面,json很坑的,部分json.dumps存不进去的数据暂时的处理方法是将字符串的单引号转换成双引号
    @logger
    def to_save(self):
        for datamonth in self.df['datamonth'].drop_duplicates().tolist():
            df_tmp = self.df[self.df['datamonth'] == datamonth]

            self.param[datamonth]['brand'] = [
                dict(brand=i) for i in df_tmp.loc[df_tmp['brand'].notnull(), 'brand'].drop_duplicates().tolist() if i]

            submarket = df_tmp.loc[df_tmp['submarket'].notnull(), 'submarket'].drop_duplicates().tolist()
            t = dict()
            for i in submarket:
                if not i:
                    continue
                i = json.loads(i)
                t.update(**i)
            t = [dict(sm_id=i, submarket=t[i]) for i in t]
            self.param[datamonth]['submkt'] = t

            sku = df_tmp.loc[df_tmp['sku'].notnull(), 'sku'].drop_duplicates().tolist()
            t = dict()
            for i in sku:
                if not i:
                    continue
                i = json.loads(i)
                for j in i:
                    if j in t:
                        t[j].add(i[j])
                    else:
                        t[j] = {i[j]}

            t = {i: list(t[i]) for i in t}
            self.param[datamonth]['property'] = t

            for i in t:
                self.xy[datamonth][i] = {'from': 'sku'}

            t = dict()
            target_score = df_tmp.loc[df_tmp['target_score'].notnull(), 'target_score'].drop_duplicates().tolist()
            for i in target_score:
                if not i:
                    continue
                i = json.loads(i)
                for tag in i:
                    if not i[tag]:
                        continue
                    if tag not in t:
                        t[tag] = {'from': 'tag_score', 'value': dict()}
                    for target in i[tag]:
                        t[tag]['value'][target] = {'from': 'target_score', 'value': i[tag][target]}
            self.xy[datamonth].update(**t)

        self.df['cid'] = self.cid
        # self.df['sku'] = self.df['sku'].str.replace('\'', '\"')
        # self.df['submarket'] = self.df['submarket'].str.replace('\'', '\"')
        # self.df['tag_score'] = self.df['tag_score'].str.replace('\'', '\"')
        # self.df['model_tag_rank'] = self.df['model_tag_rank'].str.replace('\'', '\"')
        # self.df['aver_model_tag_ratings'] = self.df['aver_model_tag_ratings'].str.replace('\'', '\"')
        self.df['model_rank'] = self.df['model_rank'].fillna(0).astype("int")
        self.df['top_model'] = self.df['top_model'].fillna(0).astype("int")
        self.df = self.df.reindex(
            columns=['cid',
                     'brand',
                     'model',
                     'datamonth',
                     'price',
                     'biz30day',
                     'total_sold_price',
                     'sku',
                     'submarket',
                     'tag_score',
                     'target_score',
                     'rate_ring_biz30day',
                     'rate_ring_total_sold_price',
                     'season_biz30day_raise',
                     'season_total_sold_price_raise',
                     'rate_year_biz30day',
                     'rate_year_total_sold_price',
                     'biz30day_increment',
                     'total_sold_price_increment',
                     'model_ratings',
                     'model_tag_ratings',
                     'model_target_ratings',
                     'aver_model_ratings',
                     'aver_model_tag_ratings',
                     'aver_model_target_ratings',
                     'model_rank',
                     'model_tag_rank',
                     'model_target_rank',
                     'top_model',
                     'top_tag',
                     'top_target',
                     'imageurl'
                     ])
        self.df = self.df.fillna("")
        self.df = self.df.drop_duplicates()
        del_sql = ("delete from {} where cid = {}".format(self.reviews_tab, self.cid))
        db_99_psql('report_dg', del_sql)
        self.df['model_rank'] = self.df['model_rank'].apply(lambda x: '%d' % x if x else '').astype(str)
        self.df['top_model'] = self.df['top_model'].apply(lambda x: '%d' % x if x else '').astype(str)
        postgres_save_df(format_value(self.df), self.engine_dg, self.reviews_tab, quotechar="", quoting=3, null='')
        log.logger.info("insert into {} cid{} total:{}".format(self.reviews_tab, self.cid, len(self.df)))

        data = []
        for i in self.xy:
            data.append([self.pcid, self.cid, self.param[i], self.xy[i], i])
        df = pd.DataFrame(data, columns=['pcid', 'cid', 'param', 'xy', 'datamonth'])
        table = 'product_brain.param_xy'
        sql = "delete from {} where pcid = {} and cid = {}".format(table, self.pcid, self.cid)
        db_psql(self.engine_dg, sql)
        df.to_sql(
            table.split('.')[1], self.engine_dg, schema=table.split('.')[0], if_exists='append', index=False,
            dtype=dict(xy=JSON, param=JSON),
        )

    def to_tencent_save(self, db, df, tabel):
        sql = "INSERT INTO " + tabel + " values " + "("
        # conn = psycopg2.connect(database=db, user="zczx_admin", password="zczx112211",
        #                         host='postgres-lkr70ecv.gz.cdb.myqcloud.com', port='62')
        conn = psycopg2.connect(database=db, user="zczx_admin", password="zczx112211",
                                host='postgres-j0ricntx.sql.tencentcdb.com', port='34831')
        status = False
        # try:
        cur = conn.cursor()
        column = list(df.columns)
        num = 0
        new_sql = ""
        total = df.count().max()
        for k, v in df.iterrows():
            num += 1
            for i in column:
                if isinstance(v[i], str) and re.search("'", v[i]):
                    tmp = v[i].split("'")
                    tmp = "''".join(tmp)
                    new_sql += "'{}',".format(tmp)
                elif v[i] in ["NULL", "", "nan", "NaN", "NAN", 'None', 'none', np.nan]:
                    new_sql += "NULL,"
                elif isinstance(v[i], float) and v[i] != [""]:
                    new_sql += '{},'.format(v[i])
                elif v[i] is None:
                    new_sql += "NULL,"
                elif isinstance(v[i], int) and v[i] != [""]:
                    new_sql += '{},'.format(v[i])
                elif isinstance(v[i], dict) and v[i] != [""] and v[i] is not None:
                    tmp = json.dumps(v[i], ensure_ascii=False)
                    # tmp = str(v[i]).split("'")
                    # tmp = '"'.join(tmp)
                    new_sql += "'{}',".format(tmp)
                else:
                    new_sql += "'{}',".format(v[i])
            new_sql = new_sql[:-1] + '), ('
            if num % 1001 == 0 and num != total:
                new_sql = sql + new_sql[:-3] + ";"
                cur.execute(new_sql)
                new_sql = ""
            if num == total:
                new_sql = sql + new_sql[:-3] + ";"
                cur.execute(new_sql)
                new_sql = ""
        conn.commit()

    def migrate_tencent(self):
        # 价格段
        sql = ("select * from product_brain.product_brain_pcid{} where cid = {}".format(self.pcid, self.cid))
        df = pd.read_sql_query(sql, self.engine_dg)
        df = df.fillna('')
        del_sql = ("delete from product_brain.product_brain_pcid{} where cid = {}".format(self.pcid, self.cid))
        if db_tencent_psql('report_dg', del_sql):
            self.to_tencent_save('report_dg', df, 'product_brain.product_brain_pcid{}'.format(self.pcid))
            log.logger.info("insert into {} cid {} total:{}".format(
                'product_brain.product_brain_pcid{}'.format(self.pcid), self.cid, len(df)))
        del df

    def run(self):
        self.get_sku()
        log.logger.info('已经获取sku')
        self.get_submarket()
        self.get_compute()
        log.logger.info('已经获取submarket')
        self.get_comment()
        log.logger.info('清理重复数据完毕,开始导入数据库')
        self.to_save()
        log.logger.info('保存数据库成功')
        obj = Confidence(pcid=self.pcid, cid=self.cid)
        obj.run()
        # self.migrate_tencent()

    def revise_99(self):
        sql = (
            "UPDATE {} SET model_rank = NULL, top_model = NULL"
            " WHERE model_rank = '0' and top_model = '0' and cid = '{}'"
        ).format(self.reviews_tab, self.cid)
        db_99_psql('report_dg', sql)


if __name__ == '__main__':
    # sbt = CreateModelReviews(2, 50008881)
    # sbt = CreateModelReviews(4, 50012097)
    sbt = CreateModelReviews(7, 50006219)
    # sbt = CreateModelReviews(4, 50004396)
    sbt.run()
    sbt.revise_99()
