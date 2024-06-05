
import numpy as np



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