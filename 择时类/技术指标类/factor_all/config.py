# -*- coding: utf-8 -*-
# coding=utf-8
# 主要功能：本地config设置

CONFIG = {
    # # ——————————全局配置项，整体策略（非各个子账号）统一配置项：——————————
    # 全局配置说明：配置项对所有子账户、所有账户类型、所有标的同时有效；不能单独指定某个单独子账户、单独账户类型、单独标的进行特定设置；
    # 动态修改方法：可以在factor_dict中重新赋值；也可以使用set_option_global(context, configs)修改；
    # 配置方法适用配置项：适用于当前位置到"分账户编号控制配置"前所有配置项；
    "cal_model_dir":"../../../",
    "output_model_dir":"../../../../",
    # 结果输出路径
    "output_dir": "result/",
    # 回测开始日期；支持'年-月-日'['2018-11-23']、'年-月-日 时:分:秒'['2018-11-23 11:12:13']、'年-月-日 时:分:秒.毫秒'['2018-11-23 11:12:13.12345']格式;
    "start_date": '2018-01-01',
    # 回测结束日期；支持'年-月-日'['2018-11-23']、'年-月-日 时:分:秒'['2018-11-23 11:12:13']、'年-月-日 时:分:秒.毫秒'['2018-11-23 11:12:13.12345']格式;
    "end_date": '2019-12-31',  # , '2021-05-25'    2018-12-31
    # 两张表index的合并方式：1：取ret_tb、factor_tb 的index并集； 2:取ret_tb的index；3：取factor_tb的index；4：取ret_tb、factor_tb 的index交集
    "merge_type": "right",# merge_type可为'outer'：两者并集，'left':价格表为索引， 'right':因子表为索引，'inner'：两者交集
    # 一年包含的数据条数（一个周期内含有的日期数量）；如日频数据中，自然日365，工作日252，周度52，月度12，季度4，半年度2；
    "period": "D",
    "winlen": 12,
    # 子账户数（即分组测试的分组数量）
    "subportfolio_num": 5,
    # 是否设置多空子账户（多空分组）：[]中值为所在子账户的subportfolio_index（即分组的编号）；如果不设置，则值为None。
    "long": 1,  # 多头，值为对应子账号（分组）编号
    "short": 2,  # 空头，值为对应子账号（分组）编号
    # 回测基准，字典
    "benchmark": {"000300.XSHG": 0.1},  # {"000300.XSHG": 1}    {"000300.XSHG": 0.7, "110044.XSHG": 0.3}
    # IC生成类型，一个列表，可以为空；pipeline中使用；
    # 可选值：["IC_all_crossSection", "IC_subportfolio_crossSection", "IC_subportfolio_retRatio"]
    "IC_types": ["IC_all_crossSection", "IC_subportfolio_crossSection", "IC_subportfolio_retRatio"],
    # IC滞后值，可以是list或者int，也可以置空；pipeline中使用；
    "IC_lag_n": [1, 2, 3],

    # all_factor层是否并行，只在all_factor_Demo使用，pipeline、backtest中不使用；
    "multiProcess_all_factor": False,
    # multi_run层是否并行
    "multiProcess_multiRun": True,  # False

    # 是否在run()层输出结果     # ys:暂未使用，run()层结果直接返回到 multi_run 层进行合并了。
    "output_run": True,

    # # ——————————全局配置项：全局回测频率控制：——————————
    # 全局回测频率控制通用说明；为0、为空表示不控制频率；可选值：minutely、daily、weekly、monthly、quantly、half_yearly、yearly、正整数值间隔；

    # 回测周期；为0、为空表示不控制频率；
    "FREQUENCY_INTERVAL": 'M',
    # 1 "daily" "time_rule(yearMonth=[11,12], monthDay=[27,28], weekDay=[], time=['10:00', '0:00'], force=True)"
    "freq_position": 'end',  # 变频取值，'end'代表取周期最后一天，'start’代表取周期第一天。该取值方式加上第一个数据

}

config_custom = {
    # # ——————————自定义配置项：——————————
    # 自定义配置项说明：因子自有配置项，只能在因子空间主动使用，不进backtest，不一定出现在远端config中。
    # 动态修改方法：可以在factor_dict中重新赋值；也可以set_option_instrument(context, conditions, ref=None)修改；
    "func_name":"择时类-技术指标类",
    "data_dir":"data",
    # 结果输出路径
    "output_dir": "result/",
    "func_dir": "factors",

    # 因子字典集；
    # # # 每个因子必须给出的参数如下（其它参数可自行增减）：
    # # "factor_dict": [{"func_name_factor": "因子名称、因子名称_signal", # 此处必须有
    # #                  "param_dataSrc": {"func_name_dataSrc": "read_file",    # 必须有；通用配置和此处设置，两种可都有，或至少选其一；
    # #                                    "colName_dataSrc": ['trade_date', 'close', 'ret']},  # 必须有；通用配置和此处设置，两种可都有，或至少选其一；必须是单值或单值构成的list，不能有键值对！！！
    # #                  "param_factor": {"参数1": "参数值", "参数2": "参数值"},  # 非必须；根据因子需要可选；
    # #                  "file_name_model": ["factor_RSJ"],  # 必须有；通用配置和此处设置，两种可都有，或至少选其一；
    # #                  # 说明：在"param_dataSrc"外部的配置项，除规定的排除项外，也会默认添加到"param_dataSrc"的list中的每个集合内，并传入dataGet中供调用；
    # #                  # # 如果想让"param_dataSrc"的list中的每个字典有特有配置项，，则需要单独在该集合中单独添加或指定；
    # #                  }],
    "factor_dict": [
              {"func_name_factor": "chaikin_oscillator_signal",
               "param_dataSrc": {"func_name_dataSrc": "price_tb.csv","colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "param_factor": {"periods_short": 3, "periods_long": 10},
               "file_name_model": "factors",
               },

              {"func_name_factor": "DMI_signal",
               "param_dataSrc": {"func_name_dataSrc": "price_tb.csv","colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "param_factor": {"period": 14, "smooth_period": 6},
               "file_name_model": "factors",
               },

              {"func_name_factor": "OBV_signal",
               "param_dataSrc": {"func_name_dataSrc": "price_tb.csv","colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "file_name_model": "factors",
               },
                {"func_name_factor": "BSM_signal",
                 "param_dataSrc": [
                     {"func_name_dataSrc": "price_tb.csv",
                      "colName_dataSrc": [{'date': 'trade_date'}, 'close', 'high', 'low', 'open', {'volume': 'vol'}],
                      "security": '000300.XSHG', "data_usage_purpose": 'signal'},
                 ],
                 "param_factor": {},
                 "file_name_model": "factors",
                 },
    ],

}


