import pandas as pd
import numpy as np

def chaikin_oscillator(data, periods_short=3, periods_long=10, high_col='high',
                       low_col='low', close_col='close', vol_col='volume'):
    """
    出处：《股票-技术指标类-Chaikin Oscillato》
        根据日频收盘价、开盘价、最高价、最低价计算DMI指标；
        若DMI大于零且比上一天增加，则发出多头信号；
        若DMI小于零且比上一天减少，反之发出空头信号；
        基于指标发出的交易信号，在第二天完成交易；
        持仓直到发出相反的交易信号，然后重复上述步骤。
    :param date, DataFrame: 计算的原始数据；
    :param periods_short, int: 计算指数加权时短窗长；
    :param periods_long, int: 计算指数加权时长窗长；
    :param high_col, str: 指定列名;
    :param low_col, str: 指定列名;
    :param close_col, str: 指定列名;
    :param vol_col, str: 指定列名；
    :return: data: 返回指标计算结果；
    """
    # 初始化存储空间
    ac = pd.Series([],dtype='float64')
    # 先设置上一个val为0
    val_last = 0
    # 对每一行，日期index
    for index, row in data.iterrows():
        # 若最高价不等于最低价，计算val值
        if row[high_col] != row[low_col]:
            val = val_last + ((row[close_col] - row[low_col]) - (row[high_col] - row[close_col])) / (
                        row[high_col] - row[low_col]) * row[vol_col]
        # 否则指定val为上一个val值
        else:
            val = val_last
        # 将当前日期的val值赋给ac对应日期
        ac[index]=val
        # 更新上一个val值
        val_last = val
    # 计算长窗长指数平均
    ema_long = ac.ewm(ignore_na=False, min_periods=0, com=periods_long, adjust=True).mean()
    # 计算短窗长指数平均
    ema_short = ac.ewm(ignore_na=False, min_periods=0, com=periods_short, adjust=True).mean()
    # 计算佳庆指标
    data['ch_osc'] = ema_short - ema_long
    # 计算90日均线
    data['SMA_90'] = data.close.rolling(90).mean().shift(1)
    return data


def chaikin_oscillator_signal(df, indicator_name='ch_osc',close_name='close',lossratio=999):
    """
    出处：《股票-技术指标类-Chaikin Oscillato》
        根据Chaikin Oscillato指标生成交易信号。
    :param df, Series: 计算的原始数据；
    :param indicator_name, str: 指定指标列名；
    :param close_name, str: 指定标的价格基准列名；
    :return: lossratio, float: 最大损失率，超过平仓则止损；
    """
    # 获取日期
    dfdate = df.index
    # 增加一列日期
    df['date'] = df.index
    # 调用因子计算指标值
    pdatas=chaikin_oscillator(df)
    # 重新设定日期索引
    pdatas.index = dfdate
    # 记录持仓
    pdatas['position'] = 0
    # 记录买卖
    pdatas['flag'] = 0
    # 设置索引为日期
    dfdate = pdatas.index
    # 记录买入价位
    pricein = []
    # 记录卖出价位
    priceout = []
    # 设置初始买入价格，足够低即可
    price_in = 1
    # 对产生90日均线后的每个日期
    for i in range(90, pdatas.shape[0] - 1):
        # 当前无仓位，Chaikin Oscillator上穿0，且股价高于90天移动平均，做多
        if (pdatas[indicator_name][dfdate[i-1]] < 0) & (pdatas[indicator_name][dfdate[i]] > 0) & (
                pdatas[close_name][dfdate[i]] > pdatas.SMA_90[dfdate[i]]) & (pdatas.position[dfdate[i]] == 0):
            # 更新买卖
            pdatas.loc[dfdate[i], 'flag'] = 1
            # 更新持仓
            pdatas.loc[dfdate[i+1], 'position'] = 1
            # 存储买入日期和价格
            pricein.append([pdatas.date[dfdate[i]], pdatas.loc[dfdate[i], close_name]])
        # 当前持仓，下跌超出止损率，止损
        elif (pdatas.position[dfdate[i]] == 1) & (pdatas[close_name][dfdate[i]] / price_in - 1 < -lossratio):
            # 更新买卖
            pdatas.loc[dfdate[i], 'flag'] = -1
            # 更新持仓
            pdatas.loc[dfdate[i+1], 'position'] = 0
            # 更新卖出价位和日期
            priceout.append([pdatas.date[dfdate[i]], pdatas.loc[dfdate[i], close_name]])
        # 当前持仓，Chaikin Oscillator下穿0，且股价低于90天移动平均，平仓
        elif (pdatas[indicator_name][dfdate[i-1]] > 0) & (pdatas[close_name][dfdate[i]] < pdatas.SMA_90[dfdate[i]]) & (
                pdatas[indicator_name][dfdate[i]] < 0) & (pdatas.position[dfdate[i]] == 1):
            # 更新买卖
            pdatas.loc[dfdate[i], 'flag'] = -1
            # 更新持仓
            pdatas.loc[dfdate[i+1], 'position'] = 0
            # 更新买卖价位和日期
            priceout.append([pdatas.date[dfdate[i]], pdatas.loc[dfdate[i], close_name]])
        # 其他情况，保持之前仓位不变
        else:
            pdatas.loc[dfdate[i+1], 'position'] = pdatas.loc[dfdate[i], 'position']
        # 获得交易信号，统一格式为±1
        signal = pdatas['position'].replace(0,-1)
    # 返回交易信号
    return signal