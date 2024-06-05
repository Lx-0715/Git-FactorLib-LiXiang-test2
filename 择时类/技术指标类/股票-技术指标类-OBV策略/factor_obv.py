# coding: utf-8
# Python 3.6
import numpy as np
import pandas as pd
def OBV(df):
    """
    出处：《股票-技术指标类-OBV策略》
        根据日频收盘价和成交量计算OBV指标；
        若OBV大于零，则发出多头信号，反之发出空头信号；
        基于指标发出的交易信号，在第二天完成交易；
        持仓直到发出相反的交易信号，然后重复上述步骤。
    :param df, Series: 计算的原始数据,索引需要是日期；
    :return: OBV, Series: OBV计算结果；
    """
    # 获取收盘价
    dfclose = df['close']
    # 获取成交量
    dfvol = df['volume']
    # 计算差分
    difClose = dfclose.diff()
    # 差分会导致向量第一个元素为nan，设置为0
    difClose[0] = 0
    # 计算OBV
    OBV = (((difClose >= 0) * 2 - 1) * dfvol).cumsum()
    # 指定列名
    OBV.name = 'OBV'
    # 保存至数据框并输出
    OBV.index = pd.to_datetime(OBV.index)
    return OBV

def OBV_signal(df):
    """
    出处：《股票-技术指标类-OBV策略》
        生成OBV交易信号。
    :param df, Series: 计算的原始数据,索引需要是日期；
    :return: signal, Series: 基于obv计算得到的交易信号；
    """
    # 调用OBV因子，计算OBV
    OBV_val = OBV(df)
    # 生成交易信号
    signal = (2 * (OBV_val.diff() > 0) - 1)[1:]
    # 差分会导致第一个元素为nan，设置为0
    signal[0] = 0
    return signal