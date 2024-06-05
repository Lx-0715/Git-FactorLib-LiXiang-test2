from dateutil.parser import parse
import pandas as pd
import numpy as np

def init_trade_cal(date_range_src, start_date, end_date):
    """
    初始化交易日历，选择给定日期范围内的交易日期
    参数:
    date_range_src: DataFrame, 原始日期数据表
    start_date: str, 开始日期
    end_date: str, 结束日期
    返回值:
    DataFrame, 经过筛选后的日期数据表
    """
    # 将日期数据转换为日期时间格式，并去除重复值并排序
    date_range_src = pd.to_datetime(date_range_src).drop_duplicates().sort_values()
    start_date = parse(start_date)
    end_date = parse(end_date)
    # 使用布尔索引选择在开始和结束日期之间的日期
    date_range_src = date_range_src[(date_range_src >= start_date) & (date_range_src <= end_date)]
    return date_range_src

def infer_period(date_range_src, period):
    # 推断日期范围的频率
    freq = pd.infer_freq(date_range_src)
    if freq is None:
        return "Unknown"
    else:
        return period

def date_range(price_tb, factor_tb, date_range_src):
    """
    选择给定日期范围内的价格和因子数据
    参数:
    price_tb: DataFrame, 价格数据表
    factor_tb: DataFrame, 因子数据表
    date_range_src: DataFrame, 日期数据表
    返回值:
    DataFrame, 经过筛选后的价格数据表和因子数据表
    """
    # 将价格和因子数据表的索引转换为日期时间格式
    price_tb.index = pd.to_datetime(price_tb.index)
    factor_tb.index = pd.to_datetime(factor_tb.index)
    # 重构价格和因子数据表，使其索引与日期数据表一致
    price_tb = price_tb.reindex(date_range_src)
    factor_tb = factor_tb.reindex(date_range_src)
    return price_tb, factor_tb

def transform_frequency(FREQUENCY_INTERVAL, date_range_src, freq_position='start'):
    """
    改变频率并设置时间间隔
    参数:
    FREQUENCY_INTERVAL: str, 改变后的频率，可选值为 ['minutely', 'daily', 'weekly', 'monthly', 'quarterly', 'half_yearly', 'yearly']，或者一个正整数值表示间隔，如果为 None，则不进行频率转换
    date_range_src: DatetimeIndex, 输入数据的索引
    freq_position: str, 可选，'start' 或 'end'，表示选择每个采样周期的第一个值或最后一个值
    """
    if FREQUENCY_INTERVAL is not None:
        if isinstance(FREQUENCY_INTERVAL, int):
            # 如果频率间隔是整数，转换为以天为单位的字符串
            freq_str = f'{FREQUENCY_INTERVAL}D'
        else:
            freq_str = FREQUENCY_INTERVAL
        # 将日期范围转换为 Series 对象，然后进行重采样
        date_range_src = pd.Series(date_range_src, index=date_range_src)
        if freq_position == 'start':
            # 使用 first 方法获取每个采样周期的第一个非 NaN 值
            date_range_src = date_range_src.resample(freq_str).first()
        else:
            # 使用 last 方法获取每个采样周期的最后一个非 NaN 值
            date_range_src = date_range_src.resample(freq_str).last()
        # 将索引设置为每个频率间隔内的最后一个非 NaN 值
        date_range_src.index = date_range_src.values
    return date_range_src

def get_position_by_factor(position_tb_original, time_label=False):
    """
    根据因子数据获取持仓数据

    参数:
    position_tb_original: DataFrame, 原始的持仓数据表，交易日期，列为资产名称
    time_label: bool, 可选，是否有择时标签，默认为 False

    返回值:
    DataFrame, 重构后的持仓数据表，交易日期，列为排序后的资产
    """
    if time_label or (not time_label and len(position_tb_original.columns) == 1):
        # 创建一个空的 DataFrame，用于存储持仓数据
        position_tb = pd.DataFrame(index=position_tb_original.index, columns=[])
        for name in position_tb_original.columns:
            # 对每一列进行分组，加入列名作为一个级别
            grouped = position_tb_original.groupby(position_tb_original[name])
            for group_name, group in grouped:
                # 对于每一组，检查原始数据中的值是否与持仓数据表的列名相匹配，如果匹配，则填充 name，否则填充 None
                position_tb[f'{name}_{group_name}'] = np.where(position_tb_original.index.isin(group.index), name, None)
        # 添加一个 'total' 列，如果原始数据的任何一列不为空，则值为原始数据中最大值的列名，否则为 None
        position_tb['total'] = np.where(position_tb_original.notnull().any(axis=1), position_tb_original.idxmax(axis=1),None)
    else:
        # 创建一个空的 DataFrame，用于存储持仓数据，列名为从 1 到原始数据列数的整数
        position_tb = pd.DataFrame(index=position_tb_original.index, columns=range(1, len(position_tb_original.columns) + 1))
        for date, row in position_tb_original.iterrows():
            # 对每一行，按值降序排序，然后将索引（即资产名）添加到新的 DataFrame 中
            sorted_assets = list(row.sort_values(ascending=False, kind='mergesort').index)
            for i, asset in enumerate(sorted_assets, start=1):
                position_tb.loc[date, i] = asset
    return position_tb

def rebuild_tb_by_position(position_tb, tb, lag=0):
    """
    根据持仓数据重构因子数据表
    参数:
    position_tb: DataFrame, 持仓数据表，行为日期，列为序号，值为排序后的资产
    tb: DataFrame, 需要重构的数据表，行为日期，列为资产，值为收益率
    lag: int, 可选，收益率数据的滞后期，默认为0
    返回值:
    DataFrame, 重构后的因子数据表，行为日期，列为序号，值为收益率
    """
    # 创建一个空的DataFrame，用于存储重构后的数据
    rebuilt_tb = pd.DataFrame(index=position_tb.index, columns=position_tb.columns)
    # 获取滞后处理后的收益率数据
    returns = tb.shift(-lag)
    # 遍历持仓数据表的每一行
    for date in position_tb.index:
        try:
            # 将收益率数据填充到重构后的数据表中
            rebuilt_tb.loc[date] = position_tb.loc[date].apply(lambda x: None if pd.isnull(x) else returns.loc[date, x])
        except KeyError as e:
            print(f"KeyError: {e}. Skipping this iteration.")
    return rebuilt_tb.astype(float)
'''

def rebuild_tb_by_position(position_tb, tb, lag=0):
    return position_tb.apply(lambda series: series.apply(lambda x: None if pd.isnull(x) else tb.shift(-lag).loc[series.name, x]))
'''

def backtest(factor_tb_original, price_tb_original, date_range_src, start_date, end_date,FREQUENCY_INTERVAL,period,freq_position):
    """
        进行回测
    :param factor_tb_original, DataFrame: 原始的因子数据表，交易日期，列为标的名称
    :param price_tb_original: DataFrame, 原始的价格数据表，交易日期，列为标的名称
    :param date_range_src: list, 交易日历
    :param start_date: str, 回测开始日期
    :param end_date: str, 回测结束日期
    :param FREQUENCY_INTERVAL: str, 回测频率
    :param period: str, 回测周期
    :param freq_position: str, 频率位置
    :return: ret_tb_original, DataFrame: 原始的收益率数据表
    :return: factor_tb_original: DataFrame, 原始的因子数据表
    :return: price_tb: DataFrame, 重构后的价格数据表
    :return: ret_tb: DataFrame, 重构后的收益率数据表
    :return: factor_tb: DataFrame, 重构后的因子数据表
    :return: position_tb: DataFrame, 重构后的持仓数据表
    :return: date_range_src: list, 交易日历
    :return: period: str, 回测周期
    """
    date_range_src = init_trade_cal(date_range_src, start_date, end_date)
    if period is None:
        period = infer_period(date_range_src)

    price_tb_original, factor_tb_original = date_range(price_tb_original, factor_tb_original, date_range_src)
    ret_tb_original = price_tb_original.sort_index().pct_change()
    # 转换频率
    frequency_interval = transform_frequency(FREQUENCY_INTERVAL, date_range_src, freq_position).drop_duplicates()
    position_tb_original = factor_tb_original.reindex(frequency_interval)
    position_tb = get_position_by_factor(position_tb_original)
    position_tb = position_tb.reindex(date_range_src, method='ffill')

    #factor_tb = position_tb.applymap(lambda positions: None if pd.isnull(positions) else factor_tb_original.loc[position_tb.index, positions].shift(0))
    factor_tb = rebuild_tb_by_position(position_tb, factor_tb_original, lag=0)
    ret_tb = rebuild_tb_by_position(position_tb, ret_tb_original, lag=0)
    price_tb = rebuild_tb_by_position(position_tb, price_tb_original, lag=0)

    return ret_tb_original, factor_tb_original,price_tb,ret_tb,factor_tb,position_tb,date_range_src,period












