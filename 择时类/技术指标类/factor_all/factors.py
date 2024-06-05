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

def BSM(s, k=10, t=1, r=0.05, v=0.2):
    """
        出处：《股票-技术指标类-BSM》
        使用收盘价数据期权价格；
    :param s, float: 股票的当前价格
    :param k, float: 行权价格
    :param t, float: 到期时间，默认一年
    :param r, float: 无风险利率，默认0.05
    :param v, flaot: 波动率 默认0.2
    :return bsm_value, float: 计算出的BSM定价
    """
    # 计算d1
    d1 = (np.log(s / k) + (r + v**2 / 2) * t) / (v * np.sqrt(t))
    # 计算d2
    d2 = d1 - v * np.sqrt(t)
    # 计算bsm价格
    bsm_value = s * np.exp(-r * t) * np.exp(-v * np.sqrt(t) * np.random.normal())
    return bsm_value

def BSM_signal(data, t=1, r=0.05, v=0.2):
    """
        出处：《股票-技术指标类-BSM》
        使用收盘价数据期权价格；
        如果定价高于现在价格，认为实际价格偏高，会上涨，买入信号；
        反之发出卖出信号。
    :param data, DataFrame: 股票数据
    :return signal, Series: 交易信号
    """
    # 存储空间交易信号
    data['signal'] = 0
    # 存储空间bsm价格
    data['bsm'] = 0
    # 对每一天
    for i in range(len(data)):
        # 获得当日价格
        price = data['close'][data.index[i]]
        # 计算当日bsm
        bsm_estimate = BSM(price, price,t,r,v)
        # 记录bsm
        data.loc[data.index[i], 'bsm'] = bsm_estimate
    # 如果当日bsm估价大于实际价格，卖出，反之买入
    data['signal'] = (data['bsm'] > data['close']) * 2 - 1
    # 存储交易信号
    signal = data['signal']
    return signal