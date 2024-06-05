import pandas as pd
def merged_performance(merged_result):
    #生成因子绩效汇总表
    def process_performance_data(data, performance_type):
        """
        函数用于处理性能数据，插入 factorname 列，并按年份合并到总表中
        """
        performance_total = {}
        # 遍历每个因子
        for factor_type, factor_type_data in data.items():
            # 检查是否存在当前性能数据类型的字典
            if performance_type in factor_type_data and factor_type_data[performance_type] is not None:
                performance = factor_type_data[performance_type]
                # 遍历当前性能数据字典中的每个年份
                for year, year_data in performance.items():
                    # 检查是否存在年份数据
                    if year_data is not None:
                        # 检查该年份的总表是否已存在，如果不存在则创建一个空的 DataFrame
                        if year not in performance_total:
                            performance_total[year] = pd.DataFrame()
                        # 检查是否已存在 'factorname' 列
                        if 'factorname' in year_data.columns:
                            # 如果存在，则更新该列的值
                            year_data['factorname'] = factor_type
                        else:
                            # 如果不存在，则插入新的 'factorname' 列
                            year_data.insert(0, 'factorname', factor_type)
                        # 将该表添加到总表中
                        performance_total[year] = pd.concat([performance_total[year], year_data], ignore_index=False)
        return performance_total

    performances_total = {}
    if 'performance_total' in merged_result:
        del merged_result['performance_total']
    # 遍历 ffn_performance 等绩效包
    for performance_type in ['ffn_performance', 'empyrical_performance', 'empyrical_performance_rolling','qs_performance', 'pyf_performance','pyf_performance_rolling']:
        # 处理性能数据
        performance_total = process_performance_data(merged_result, performance_type)
        # 将处理后的性能数据加到 result 中
        performances_total[f'{performance_type}'] = performance_total
    return performances_total

