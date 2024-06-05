import pandas as pd
from config import CONFIG,config_custom
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor,as_completed
import os
import importlib
import main
import backtest_vector
import cal_metric_api

def factor_all_pipeline_time(config_custom, CONFIG):
    # ------------定义因子回测函数-------------
    def process_indicator(factor, price_tb_original, CONFIG):
        import sys
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))
        module_name = factor["file_name_model"]
        function_name = factor["func_name_factor"]
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)

        # 计算因子
        price_tb_original['flag'] = function(price_tb_original)
        price_tb = price_tb_original['close'].to_frame('stock')
        factor_tb = price_tb_original['flag'].to_frame('stock')

        # 回测
        FREQUENCY_INTERVAL = CONFIG["FREQUENCY_INTERVAL"]
        freq_position = CONFIG["freq_position"]
        benchmark = CONFIG["benchmark"]
        subportfolio_num = CONFIG["subportfolio_num"]
        IC_lag_n = CONFIG["IC_lag_n"]
        period = CONFIG["period"]
        winlen = CONFIG["winlen"]
        start_date = CONFIG["start_date"]
        end_date = CONFIG["end_date"]


        # 调用 backtest
        date_range_src = price_tb.index
        ret_tb_original, factor_tb_original, price_tb, ret_tb, factor_tb, position_tb, date_range_src, period = backtest_vector.backtest(factor_tb, price_tb, date_range_src, start_date, end_date, FREQUENCY_INTERVAL, period, freq_position)

        # 调用 cal_metric
        cal_metric_result = cal_metric_api.cal_portfolio_metric(price_tb, ret_tb, factor_tb, position_tb, benchmark, subportfolio_num, IC_lag_n, period, winlen)

        return cal_metric_result

    # ------------回测-------------
    # --------导入数据---------
    # 计算数据目录的绝对路径
    data_dir = os.path.abspath(config_custom["data_dir"])
    # 计算文件的绝对路径
    file_path = os.path.join(data_dir, "price_tb.csv")
    # 读取数据文件
    price_tb_original = pd.read_csv(file_path)
    price_tb_original.set_index('Date', inplace=True)

    # ------循环调用回测函数-----
    cal_metric_results = {}
    # 从全局配置中获取因子列表
    factor_dicts = config_custom['factor_dict']
    # 根据全局配置决定是否使用并行计算
    if CONFIG["multiProcess_all_factor"] == "True":
        # 使用并行计算
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = []
            for factor_dict in factor_dicts:
                future = executor.submit(process_indicator, factor_dict, price_tb_original, CONFIG)
                futures.append(future)
            for future in as_completed(futures):
                function_name = factor_dict['func_name_factor']
                # 统一命名
                function_name = function_name if function_name.endswith('_signal') else function_name + '_signal'
                cal_metric_results[function_name] = future.result()

    else:
        # 使用顺序计算
        for factor_dict in factor_dicts:
            cal_metric_result = process_indicator(factor_dict, price_tb_original, CONFIG)
            function_name = factor_dict['func_name_factor']
            # 统一命名
            function_name = function_name if function_name.endswith('_signal') else function_name + '_signal'
            cal_metric_results[function_name] = cal_metric_result

    # ------------输出-------------
    sys.path.append(CONFIG["output_model_dir"])
    import output_file
    output_file_path = os.path.join(CONFIG['output_dir'], "cal_metric_indicator.pkl")
    cal_metric_results = output_file.output_func(cal_metric_results, output_file_path)

    # web分析
    return cal_metric_results

try:
    if __name__ == '__main__':
        cal_metric_results = factor_all_pipeline_time(config_custom, CONFIG)
        # 生成汇总表
        import merge_perfomance
        cal_metric_results['performance_total'] = merge_perfomance.merged_performance(cal_metric_results)
        # web分析
        app = main.create_app(cal_metric_results, CONFIG=CONFIG)
        app.run(debug=True)
except Exception as ex:
    import traceback
    import send_email
    # 发生异常时，发送邮件
    send_email.send_an_error_message(program_name='程序测试', error_name=repr(ex), error_detail=traceback.format_exc())



