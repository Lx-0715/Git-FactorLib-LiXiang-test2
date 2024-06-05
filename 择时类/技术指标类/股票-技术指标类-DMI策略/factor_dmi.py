# coding: utf-8
# Python 3.6
import numpy as np
import pandas as pd
def DMI(df, n=14, m=6):
    """
    出处：《股票-技术指标类-DMI策略》
        根据日频收盘价、开盘价、最高价、最低价计算DMI指标；
        若DMI大于零且比上一天增加，则发出多头信号；
        若DMI小于零且比上一天减少，反之发出空头信号；
        基于指标发出的交易信号，在第二天完成交易；
        持仓直到发出相反的交易信号，然后重复上述步骤。
    :param df, Series: 计算的原始数据,索引需要是日期；
    :param m, int: 计算adx指标时滑动窗口长度；
    :param n, int: 计算trz指标时滑动窗口长度；
    :return: _dmi, Series: dmi计算结果；
    """
    # 计算真实波幅tr指标
    tr = pd.Series(np.vstack([df['high'] - df['low'], (df['high'] - df['close'].shift()).abs(),
                              (df['low'] - df['close'].shift()).abs()]).max(axis=0), index=df.index)
    # tr指标滑动窗口求和
    trz = tr.rolling(n).sum()
    # 数据存储数据框
    _m = pd.DataFrame()
    # 计算最高价差价hd
    _m['hd'] = df['high'] - df['high'].shift()
    # 计算最低价差价ld
    _m['ld'] = df['low'].shift() - df['low']
    # 若hd正且大于ld则取hd，否则取0
    _m['mp'] = _m.apply(lambda x: x.hd if x.hd > 0 and x.hd > x.ld else 0, axis=1)
    # 若ld正且大于hd则取ld，否则取0
    _m['mm'] = _m.apply(lambda x: x.ld if x.ld > 0 and x.hd < x.ld else 0, axis=1)
    # 计算mp滑动窗口求和
    _m['dmp'] = _m.mp.rolling(n).sum()
    # 计算mm滑动窗口求和
    _m['dmm'] = _m.mm.rolling(n).sum()
    # 结果数据框
    _dmi = pd.DataFrame()
    # 开盘价
    _dmi['open'] = df['open']
    #收盘价
    _dmi['close'] = df['close']
    # 计算pdi指标
    _dmi['pdi'] = 100 * _m.dmp.div(trz)
    # 计算mdi指标
    _dmi['mdi'] = 100 * _m.dmm.div(trz)
    # 计算adx指标
    _dmi['adx'] = ((_dmi.mdi - _dmi.pdi).abs() / (_dmi.mdi + _dmi.pdi) * 100).rolling(m).mean()
    # 计算adxr指标
    _dmi['adxr'] = (_dmi.adx + _dmi.adx.shift(m)) / 2
    # 设置索引
    _dmi.index = df.index
    # 去掉nan值所在行
    _dmi = _dmi.dropna()
    # 计算dmi指标
    _dmi['dmi'] = _dmi['pdi'] - _dmi['mdi']
    # 初始化策略side
    _dmi['side'] = -1
    # 返回dmi计算结果
    return _dmi

def DMI_signal(df):
    """
    出处：《股票-技术指标类-DMI策略》
        根据DMI指标生成交易信号。
    :param df, Series: 计算的原始数据,索引需要是日期；
    :param m, int: 窗长；
    :return: signal, Series: 基于DMI计算得到的交易信号；
    """
    # 调用DMI因子，计算DMI
    dmi = DMI(df)
    # 获取dmi长度c
    c = len(dmi)
    # 根据dmi索引获得日期
    dmidate = dmi.index
    # 对每一个日期
    for i in range(len(dmidate)):
        # 第1天后，倒数第二天前
        if i > 1 and i + 1 < len(dmidate):
            # 若dmi正且增加，购入
            if dmi.loc[dmidate[i],'dmi'] > 0 and dmi.loc[dmidate[i],'dmi'] > dmi.loc[dmidate[i-1],'dmi']:
                dmi['side'].values[i] = 1
            # 若dmi负且减小，卖出
            if dmi.loc[dmidate[i],'dmi'] < 0 and dmi.loc[dmidate[i],'dmi'] < dmi.loc[dmidate[i-1],'dmi']:
                dmi['side'].values[i] = -1
    # 获得交易信号
    signal = dmi['side']
    # 返回交易信号
    return signal






