# -*- coding: utf-8 -*-
# coding=utf-8
# 主要功能：本地config设置


# 本地总CONFIG
CONFIG = {
    # # ——————————全局配置项，整体策略（非各个子账号）统一配置项：——————————
    # 全局配置说明：配置项对所有子账户、所有账户类型、所有标的同时有效；不能单独指定某个单独子账户、单独账户类型、单独标的进行特定设置；
    # 动态修改方法：可以在factor_dict中重新赋值；也可以使用set_option_global(context, configs)修改；
    # 配置方法适用配置项：适用于当前位置到"分账户编号控制配置"前所有配置项；

    # 因子、策略所在文件夹名称、路径；
    "factor_path": ["all_factor"],  # ["all_factor","选股类","择时类"]
    # 因子中文名称；如果为空，会用"func_name_factor"的非空值填充；
    "factor_name": ["所有因子"],
    # 数据存放路径
    "data_dir": "../data",
    # 因子值、交易数据、交易日期等结果输出路径
    "factor_dir": ["all_factor/result/"],
    # 模型路径，模型算法文件所在文件夹名称；用于机器学习等抽取出来的统一模型文件存放的路径；作为import时的路径；
    "cal_model_dir":"/",
    "output_model_dir":"../../",
    # 结果输出路径
    "output_dir": "../result/",
    # 回测开始日期；支持'年-月-日'['2018-11-23']、'年-月-日 时:分:秒'['2018-11-23 11:12:13']、'年-月-日 时:分:秒.毫秒'['2018-11-23 11:12:13.12345']格式;
    "start_date": '2018-01-01',
    # 回测结束日期；支持'年-月-日'['2018-11-23']、'年-月-日 时:分:秒'['2018-11-23 11:12:13']、'年-月-日 时:分:秒.毫秒'['2018-11-23 11:12:13.12345']格式;
    "end_date": '2019-12-31',  # , '2021-05-25'    2018-12-31
    "merge_type": "right",# merge_type可为'outer'：两者并集，'left':价格表为索引， 'right':因子表为索引，'inner'：两者交集
    # 一年包含的数据条数（一个周期内含有的日期数量）；如日频数据中，自然日365，工作日252，周度52，月度12，季度4，半年度2；
    "period": 252,
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
    "IC_lag_n": [1, 2, 3],  # [1,2,3]

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

    # 因子函数名称；可能与factor_name不止相差"_signal"，如信号为多个因子组合生成时；
    "func_name_factor": [],
    # 源数据获取函数名称；注意：dataGet_DB.py中的query_DB只能在factor_all中使用，单因子测试需使用其它函数直接调用离线数据文件；
    "func_name_dataSrc": [],
    # 因子参数
    "param_factor": [],
    # 源数据参数，保存读取源数据的字典集；该字段内包含的参数将送入数据获取函数进行源数据的各种处理；
    # 已默认添加配置项，会将对应的原始键值对（无论是factor_dict还是CONFIG中）在因子无指定时赋值到该“源数据参数”中；
    # 默认添加配置项如下：["data_dir", "benchmark", "universe", "universe_trade", "universe_signal", "security", "security_trade", "security_signal",
    #   "strategy_type", "colName_dataSrc", "colName_derived_ref", "file_name_dataSrc", "func_name_dataSrc", "data_usage_purpose", "file_name_factor_IO", "colName_field_mapping"]
    # todo：需要测试该字段是否需要支持list中带多组集合的情形，即完整取数的参数组合，是否有足够多应用场景？？？如果需要，则需要将该配置项合并？还是覆盖到"factor_dict"中对应字段？
    "param_dataSrc": [],

    # # "colName_dataSrc" 和 "colName_derived"共同构成用于因子源数据输入字段；为源数据必须直接包含的因子需要的字段；如果没有因子所需要的字段，则不启动计算该因子。
    # # # 如果此处和factor_dict中都为空，表示不限制输入字段数量，如机器学习中，输入特征数量可以不限制；
    # 支持单值、键值对构成的列表。因子需要的源数据的列名、数据字段，即可以从源数据库中直接获取到的字段；对应数据库可以直接获取的列，或通过列名映射可以直接获取的列；
    # 示例：'date','因子字段名', {'date':'trade_date'}, {'因子字段名':'源数据列名'}, {'因子字段名':{'源数据表名':'源数据字段名'}}
    # 不要轻易加源数据表名，源数据表名会限制因子跨品种测试；
    "colName_dataSrc": [],  # ['open', 'trade_date', 'unit_net_value']
    # 因子需要的衍生指标的列名、数据字段，即源数据库中没有该字段，需自行计算并生成的衍生指标。
    "colName_derived": [],  # ['ret']
    # 因子衍生指标计算需要参考的列,对该列进行各种衍生指标的计算和变形；
    "colName_derived_ref": [],  # ['close']，用于生成衍生字段['ret']时使用；
    # 回测中使用的交易价格对应列名；
    "colName_tradePrice": ['close'],  # ['close']，用于生成衍生字段['ret']时使用；
    # 回测中使用的基准价格对应列名；
    "colName_benchmarkPrice": ['close'],  # ['close']，用于生成衍生字段['ret']时使用；
    # 列名所在数据库表的名称;获取数据时，除带有frequency的行情数据字段外，其它列名优先从如下数据库表中查找；
    "DB_tb_name": [],  # "income", ["income", "balancesheet"]
    # 从数据库获取的多张表合并模式，bool型，可选项[True, False]，为True用concat，为False用merge；
    "DB_tb_concat_flag": [False],
    # 源数据频率，使用dataGet_DB时必须给值（通用配置或因子私有配置）；Tushare_DB可选项["daily", "weekly", "monthly", "mins"];
    "data_frequency": ["daily"],  #
    # 数据用途：用于交易、生成信号；默认为空，为同时用于生成信号和交易；可选项：'trade', '择时类', []空值；
    "data_usage_purpose": [],
    # 源数据文件名称
    "file_name": [],
    # 源数据文件名称
    "file_name_dataSrc": [],
    # 输入和输出的因子文件名称；命名规则为"func_name_factor"__"universe"__"security",存储在"factor_dir"中;
    "file_name_factor_IO": [],
    # 模型文件名称，模型文件名称要使用模型本身名称来直接命名；作为import引入时使用,不带后缀；如果有相对路径，需要加上；
    # 如因子存放在"factor_RSJ.py"中，则需要import该模型文件，
    # 策略类型
    "strategy_type": [],  # "日频"  "日内高频"
    # 策略方法类型;可选值:"择时"、"选股类"、"资产配置"、"机器学习和深度学习"
    "strategy_method_type": [],
    # 策略类型；可选值："技术指标"、"动量"、"反转"、"配对交易"、"高频投资"、"算法交易"、"套利"等；、
    "strategy_indicators_type": [],

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
    "func_name":"全因子回测",
    "factor_dict": [
              #择时类
              {"func_name_factor": "Chaikin Oscillator策略",
               "param_dataSrc": {"file_name": "price_tb.csv",
                                 "colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "param_factor": {"periods_short": 3, "periods_long": 10},
               "file_name_model": "Chaikin_Oscillator",
               "data_dir":"择时类/技术指标类/股票-技术指标类-Chaikin Oscillator/data",
               "func_dir": "择时类/技术指标类/股票-技术指标类-Chaikin Oscillator/",
               },

              {"func_name_factor": "DMI策略",
               "param_dataSrc": {"file_name": "price_tb.csv",
                                 "colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "param_factor": {"period": 14, "smooth_period": 6},
               "file_name_model": "DMI",
               "data_dir":"择时类/技术指标类/股票-技术指标类-DMI策略/data",
               "func_dir": "择时类/技术指标类/股票-技术指标类-DMI策略/",
               },

              {"func_name_factor": "OBV策略",
               "param_dataSrc": {"file_name": "price_tb.csv",
                                 "colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "file_name_model": "OBV",
               "data_dir":"择时类/技术指标类/股票-技术指标类-OBV策略/data",
               "func_dir":"择时类/技术指标类/股票-技术指标类-OBV策略/"
               },

                {"func_name_factor": "SMOBV策略",
               "param_dataSrc": {"file_name": "price_tb.csv",
                                 "colName_dataSrc": ['Date', 'open', 'high', 'low', 'close', 'adj_close', 'vol']},
               "param_factor": {"window": 9},
               "file_name_model": "SMOBV",
               "data_dir":"择时类/技术指标类/股票-技术指标类-OBV策略/data",
               "func_dir":"择时类/技术指标类/股票-技术指标类-OBV策略/"
               },

               #选股类
               {"func_name_factor": ['alpha009', 'alpha010', 'alpha019'],
               "param_dataSrc": {"file_name": 'price_tb.csv', "colName_dataSrc": ['date', 'ret']},
               "file_name_model": "Alpha_101",
               "data_dir":"选股类/交易所指标类/Alpha_101/data",
               "func_dir":"选股类/交易所指标类/Alpha_101/",
               }],
}



