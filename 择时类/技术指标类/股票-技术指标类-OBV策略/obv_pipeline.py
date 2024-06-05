import pandas as pd
from config import CONFIG,config_custom
import sys
import os
import main

def obv_pipeline(config_custom, CONFIG):
    # ------------数据获取/处理-------------
    factor_dicts = config_custom['factor_dict']
    cal_metric_result = {}
    for factor in factor_dicts:
        # 计算数据目录的绝对路径
        data_dir = os.path.abspath(config_custom["data_dir"])
        # 计算文件的绝对路径
        file_path = os.path.join(data_dir, factor["param_dataSrc"]["func_name_dataSrc"])
        # 读取数据文件
        price_tb_original = pd.read_csv(file_path)
        price_tb_original.set_index('Date', inplace=True)

        # ------------因子计算-------------
        import importlib
        import sys
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        module_name = factor["file_name_model"]
        function_name = factor["func_name_factor"]
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        # 计算交易信号
        price_tb_original['flag'] = function(price_tb_original)
        price_tb = price_tb_original['close'].to_frame('stock')
        factor_tb = price_tb_original['flag'].to_frame('stock')

        # ------------回测-------------
        sys.path.append(CONFIG["cal_model_dir"])
        FREQUENCY_INTERVAL = CONFIG["FREQUENCY_INTERVAL"]
        freq_position = CONFIG["freq_position"]
        benchmark = CONFIG["benchmark"]
        subportfolio_num = CONFIG["subportfolio_num"]
        IC_lag_n = CONFIG["IC_lag_n"]
        period = CONFIG["period"]
        winlen = CONFIG["winlen"]
        start_date = CONFIG["start_date"]
        end_date = CONFIG["end_date"]
        # 统一命名
        function_name = function_name if function_name.endswith('_signal') else function_name + '_signal'
        # 调用 backtest
        import backtest_vector
        # 调用 cal_metric
        import cal_metric_api
        date_range_src = price_tb.index
        ret_tb_original, factor_tb_original, price_tb, ret_tb, factor_tb, position_tb, date_range_src, period = backtest_vector.backtest(factor_tb, price_tb, date_range_src, start_date, end_date, FREQUENCY_INTERVAL, period, freq_position)
        cal_metric_result[function_name] = cal_metric_api.cal_portfolio_metric(price_tb, ret_tb, factor_tb, position_tb, benchmark,subportfolio_num, IC_lag_n, period, winlen)

    # ------------输出-------------
    sys.path.append(CONFIG["output_model_dir"])
    import output_file
    output_file_path = os.path.join(CONFIG['output_dir'], "cal_metric_indicator.pkl")
    cal_metric_result = output_file.output_func(cal_metric_result, output_file_path)

    return cal_metric_result

try:
    if __name__ == '__main__':
        cal_metric_result = obv_pipeline(config_custom,CONFIG)
        # 生成汇总表
        import merge_perfomance
        cal_metric_result['performance_total'] = merge_perfomance.merged_performance(cal_metric_result)
        # web分析
        app = main.create_app(cal_metric_result, CONFIG=CONFIG)
        app.run(debug=True)
except Exception as ex:
    import traceback
    import send_email
    # 发生异常时，发送邮件
    send_email.send_an_error_message(program_name='程序测试', error_name=repr(ex), error_detail=traceback.format_exc())

'''
if __name__ == '__main__':
    cal_metric_result = obv_pipeline(config_custom,CONFIG)
    # 生成汇总表
    import merge_perfomance
    cal_metric_result['performance_total'] = merge_perfomance.merged_performance(cal_metric_result)
    # web分析
    app = main.create_app(cal_metric_result, CONFIG=CONFIG)
    app.run(debug=True)
'''







