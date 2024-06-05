import pandas as pd
import numpy as np
from ffn.utils import fmtn, fmtp

def ffn_display_return_df(stats):
    """
    将摘要统计信息表作为 DataFrame 返回。
    :param stats,ffn.core.GroupStats: 绩效统计信息对象。
    :return: df, DataFrame: 包含摘要统计信息的 DataFrame。
    """
    # 初始化结果 data
    data = []
    # 创建 DataFrame 的第一行，这将是列名
    first_row = ["Stat"]
    first_row.extend(stats._names)
    data.append(first_row)

    # 从 stats 对象中获取统计数据
    stats_data = stats._stats()
    # 遍历 stats_data 中的每个统计数据
    for stat in stats_data:
        # 将 stat 分解为其组成部分
        k, n, f = stat
        # 如果 stat 为 None，则终止循环
        if k is None:
            continue
        # 用统计数据的名称初始化一个新行
        row = [n]
        # 遍历 stats._names 中的每个名称
        for key in stats._names:
            # 获取统计数据的原始值
            raw = getattr(stats[key], k)
            # 如果统计数据是 'rf' 并且其类型不是 float，向行中添加 NaN
            if k == "rf" and not type(raw) == float:
                row.append(np.nan)
            # 如果格式为 None，将原始值添加到行中
            elif f is None:
                row.append(raw)
            # 如果格式为 'p'，将格式化的百分比添加到行中
            elif f == "p":
                row.append(fmtp(raw))
            # 如果格式为 'n'，将格式化的数字添加到行中
            elif f == "n":
                row.append(fmtn(raw))
            elif f == "dt":
                continue
            # 如果不支持的格式，抛出错误
            else:
                raise NotImplementedError("unsupported format %s" % f)
        # 将完成的行添加到数据中
        data.append(row)
    # 将数据转换为 DataFrame 并返回
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def ffn_indicators(data):
    """
    计算给定 DataFrame 的各种性能指标。
    :param data,DataFrame: 包含基金收益率随时间变化的 DataFrame。
    :return: res, DataFrame: 基金各种指标。
    """
    # 计算基金的绩效统计指标
    stats = data.calc_stats()
    # 将指标进行处理后返回
    res = ffn_display_return_df(stats)
    return res

def ffn_metric(df):
    """
        生成每个基金统计指标信息，在进行汇总返回。
        指标包括:
        Risk-free rate: 无风险利率
        Total Return: 总回报
        Daily Sharpe: 每日夏普比率
        Daily Sortino: 每日索提诺比率
        CAGR: 复合年增长率
        Max Drawdown: 最大回撤
        Calmar Ratio: Calmar比率
        MTD: 本月至今
        3m: 3个月
        6m: 6个月
        YTD: 年初至今
        1Y: 1年
        3Y (ann.): 3年（年化）
        5Y (ann.): 5年（年化）
        10Y (ann.): 10年（年化）
        Since Incep. (ann.): 自始至今（年化）
        Daily Mean (ann.): 每日均值（年化）
        Daily Vol (ann.): 每日波动率（年化）
        Daily Skew: 每日偏度
        Daily Kurt: 每日峰度
        Best Day: 最佳日
        Worst Day: 最差日
        Monthly Sharpe: 每月夏普比率
        Monthly Sortino: 每月索提诺比率
        Monthly Mean (ann.): 每月均值（年化）
        Monthly Vol (ann.): 每月波动率（年化）
        Monthly Skew: 每月偏度
        Monthly Kurt: 每月峰度
        Best Month: 最佳月
        Worst Month: 最差月
        Yearly Sharpe: 每年夏普比率
        Yearly Sortino: 每年索提诺比率
        Yearly Mean: 每年均值
        Yearly Vol: 每年波动率
        Yearly Skew: 每年偏度
        Yearly Kurt: 每年峰度
        Best Year: 最佳年
        Worst Year: 最差年
        Avg. Drawdown: 平均回撤
        Avg. Drawdown Days: 平均回撤天数
        Avg. Up Month: 平均盈利月
        Avg. Down Month: 平均亏损月
        Win Year %: 盈利年份百分比
        Win 12m %: 过去12个月盈利百分比
    :param df, DataFrame: 基金收益率数据。
    :return:results_df, DataFrame: 包含所有基金统计信息的 DataFrame。
    """

    # 初始化结果 DataFrame
    results_df = pd.DataFrame()
    # 遍历每个基金的列
    for fund in df.iloc[:, :-1].columns:
        if df[fund].isnull().all():
            pass
        else:
            # 创建基金的单列 DataFrame
            combined_data = pd.DataFrame({fund: df[fund]}, index=df.index)
            combined_data.index.rename('Date', inplace=True)
            # 计算基金的统计信息
            fund_stats = ffn_indicators(combined_data)
            if results_df.empty:
                results_df = fund_stats
            else:
                # 仅保留结果的第二列用于拼接
                fund_stats = fund_stats.iloc[:, 1:2]
                results_df = pd.concat([results_df, fund_stats], axis=1)
    # 设置索引
    results_df.index = ['start', 'end', 'Risk-free rate', 'Total Return', 'Daily Sharpe', 'Daily Sortino', 'CAGR',
                        'Max Drawdown',
                        'Calmar Ratio', 'MTD', '3m', '6m', 'YTD', '1Y', '3Y (ann.)', '5Y (ann.)', '10Y (ann.)',
                        'Since Incep. (ann.)', 'Daily Sharpe', 'Daily Sortino', 'Daily Mean (ann.)', 'Daily Vol (ann.)',
                        'Daily Skew', 'Daily Kurt', 'Best Day', 'Worst Day', 'Monthly Sharpe', 'Monthly Sortino',
                        'Monthly Mean (ann.)', 'Monthly Vol (ann.)', 'Monthly Skew', 'Monthly Kurt', 'Best Month',
                        'Worst Month', 'Yearly Sharpe', 'Yearly Sortino', 'Yearly Mean', 'Yearly Vol', 'Yearly Skew',
                        'Yearly Kurt', 'Best Year', 'Worst Year', 'Avg. Drawdown', 'Avg. Drawdown Days',
                        'Avg. Up Month',
                        'Avg. Down Month', 'Win Year %', 'Win 12m %']
    results_df = results_df.transpose()
    # 去取第一行
    results_df = results_df.drop(results_df.index[0])
    # 删除结果中的 "start" 和 "end" 列信息
    results_df = results_df.drop(results_df.columns[[0, 1]], axis=1)
    print("ffn", results_df)
    return results_df

def quantstats_metric(df):
    """
        生成每个基金统计指标信息，在进行汇总返回。
        指标包括:
        avg_loss: 平均损失
        avg_return: 平均回报
        avg_win: 平均盈利
        best: 最佳回报
        cagr: 复合年增长率
        calmar: 卡尔马比率
        common_sense_ratio: 常识比率
        comp: 复合回报
        consecutive_losses: 连续亏损
        consecutive_wins: 连续盈利
        cpc_index: CPC指数
        expected_return: 预期回报
        exposure: 敞口
        gain_to_pain_ratio: 收益痛苦比
        geometric_mean: 几何平均数
        ghpr: 几何平均持有期收益率
        kelly_criterion: 凯利准则
        kurtosis: 峰度
        max_drawdown: 最大回撤
        outlier_loss_ratio: 异常损失比率
        outlier_win_ratio: 异常盈利比率
        payoff_ratio: 收益比率
        profit_factor: 利润因子
        profit_ratio: 利润比率
        rar: 风险调整后的回报
        recovery_factor: 恢复因子
        risk_of_ruin: 破产风险
        risk_return_ratio: 风险回报比率
        ror: 回报率
        sharpe: 夏普比率
        skew: 偏度
        sortino: 索提诺比率
        tail_ratio: 尾部比率
        ulcer_index: 溃疡指数
        ulcer_performance_index: 溃疡性能指数
        upi: UPI，即单位周期收益
        value_at_risk: 风险价值
        var: 方差
        volatility: 波动性
        win_loss_ratio: 胜败比率
        win_rate: 胜率
        worst: 最差回报
    :param df, DataFrame: 基金收盘价数据。
    :return:results_df, DataFrame: 包含所有基金统计信息的 DataFrame。
    """
    import quantstats as qs
    # 创建一个新的DataFrame，用于存储每个基金的金融指标
    results = pd.DataFrame()

    # 对每个基金进行循环
    for fund in df.iloc[:, :-1].columns:
        # 获取基金的收益率pip
        returns = df[fund]

        # 计算并存储各种量化指标
        stats = {
            'avg_loss': qs.stats.avg_loss(returns),  # 平均损失
            'avg_return': qs.stats.avg_return(returns),  # 平均回报
            'avg_win': qs.stats.avg_win(returns),  # 平均盈利
            'best': qs.stats.best(returns),  # 最佳回报
            'cagr': qs.stats.cagr(returns),  # 复合年增长率
            'calmar': qs.stats.calmar(returns),  # 卡尔马比率
            'common_sense_ratio': qs.stats.common_sense_ratio(returns),  # 常识比率
            'comp': qs.stats.comp(returns),  # 复合回报
            'consecutive_losses': qs.stats.consecutive_losses(returns),  # 连续亏损
            'consecutive_wins': qs.stats.consecutive_wins(returns),  # 连续盈利
            'cpc_index': qs.stats.cpc_index(returns),  # CPC指数
            'expected_return': qs.stats.expected_return(returns),  # 预期回报
            'exposure': qs.stats.exposure(returns),  # 敞口
            'gain_to_pain_ratio': qs.stats.gain_to_pain_ratio(returns),  # 收益痛苦比
            'geometric_mean': qs.stats.geometric_mean(returns),  # 几何平均数
            'ghpr': qs.stats.ghpr(returns),  # 几何平均持有期收益率
            'kelly_criterion': qs.stats.kelly_criterion(returns),  # 凯利准则
            'kurtosis': qs.stats.kurtosis(returns),  # 峰度
            'max_drawdown': qs.stats.max_drawdown(returns),  # 最大回撤
            'outlier_loss_ratio': qs.stats.outlier_loss_ratio(returns),  # 异常损失比率
            'outlier_win_ratio': qs.stats.outlier_win_ratio(returns),  # 异常盈利比率
            'payoff_ratio': qs.stats.payoff_ratio(returns),  # 收益比率
            'profit_factor': qs.stats.profit_factor(returns),  # 利润因子
            'profit_ratio': qs.stats.profit_ratio(returns),  # 利润比率
            'rar': qs.stats.rar(returns),  # 风险调整后的回报
            'recovery_factor': qs.stats.recovery_factor(returns),  # 恢复因子
            'risk_of_ruin': qs.stats.risk_of_ruin(returns),  # 破产风险
            'risk_return_ratio': qs.stats.risk_return_ratio(returns),  # 风险回报比率
            'ror': qs.stats.ror(returns),  # 回报率
            'sharpe': qs.stats.sharpe(returns),  # 夏普比率
            'skew': qs.stats.skew(returns),  # 偏度
            'sortino': qs.stats.sortino(returns),  # 索提诺比率
            'tail_ratio': qs.stats.tail_ratio(returns),  # 尾部比率
            'ulcer_index': qs.stats.ulcer_index(returns),  # 溃疡指数
            'ulcer_performance_index': qs.stats.ulcer_performance_index(returns),  # 溃疡性能指数
            'upi': qs.stats.upi(returns),  # UPI，即单位周期收益
            'value_at_risk': qs.stats.value_at_risk(returns),  # 风险价值
            'var': qs.stats.var(returns),  # 方差
            'volatility': qs.stats.volatility(returns),  # 波动性
            'win_loss_ratio': qs.stats.win_loss_ratio(returns),  # 胜败比率
            'win_rate': qs.stats.win_rate(returns),  # 胜率
            'worst': qs.stats.worst(returns)  # 最差回报
        }
        results = results.append(stats, ignore_index=True)

    # 设置结果DataFrame的索引为基金名称
    results.index = df.iloc[:, :-1].columns

    print("qs", results)

    # 返回包含所有金融指标的DataFrame
    return results

import empyrical as em
def empyrical_metrics(df, period):
    """
        计算并返回基本金融量化指标。

        指标包括:
        ann_return_monthly: 月度年化收益
        ann_volatility: 月度年化波动率
        cagr_ratio: 复合年增长率
        calmar_monthly: 月度Calmar比率
        cvar: 条件风险价值
        Cum_returns_final: 累积收益
        downside_risk_monthly: 月度下行风险
        max_dd: 最大回撤
        omega: Omega比率
        sortino: 索提诺比率
        stability: 时间序列的稳定性
        tail: 尾部比率
        var: 风险价值
        sharpe_monthly: 月度夏普比率
        sharpe_yearly: 年度夏普比率
    :param df, DataFrame: 基金收益率数据。
    :return: results_df, DataFrame:包含仅需基金净收益数据对应基金的基本指标值。
    """

    # 创建一个新的DataFrame来存储结果
    results_df = pd.DataFrame()
    # 设置原始频度
    if period == 'D':
        original_freq = 'daily'
    elif period == 'M':
        original_freq = 'monthly'
    elif period == 'Q':
        original_freq = 'quarterly'
    elif period == 'Y':
        original_freq = 'yearly'

    for fund in df.iloc[:, :-1].columns:
        returns = df[fund]
        if returns.isnull().all():
            pass
        else:
            # 计算各种量化指标
            cvar = em.conditional_value_at_risk(returns)  # 计算条件风险价值
            Cum_returns_final = em.cum_returns_final(returns)  # 计算最终的累积收益
            max_dd = em.max_drawdown(returns)  # 计算最大回撤
            omega = em.omega_ratio(returns)  # 计算Omega比率
            sortino = em.sortino_ratio(returns)  # 计算索提诺比率
            stability = em.stability_of_timeseries(returns)
            tail = em.tail_ratio(returns)  # 计算尾部比率
            var = em.value_at_risk(returns)  # 计算风险价值

            # 计算各种频度的指标
            for freq_type in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']:
                if freq_type == original_freq or freq_type > original_freq:
                    ann_return = em.annual_return(returns, period=freq_type)
                    ann_volatility = em.annual_volatility(returns, period=freq_type)
                    cagr_ratio = em.cagr(returns, period=freq_type)
                    calmar = em.calmar_ratio(returns, period=freq_type)
                    sharpe = em.sharpe_ratio(returns, period=freq_type)

                    # 将结果存储在新的DataFrame中
                    results_df.loc[fund, f"{freq_type}_Annual_Return"] = ann_return
                    results_df.loc[fund, f"{freq_type}_Annual_Volatility"] = ann_volatility
                    results_df.loc[fund, f"{freq_type}_CAGR_Ratio"] = cagr_ratio
                    results_df.loc[fund, f"{freq_type}_Calmar_Ratio"] = calmar
                    results_df.loc[fund, f"{freq_type}_Sharpe_Ratio"] = sharpe

        # 将其他指标存储在新的DataFrame中
        results_df.loc[fund, 'CVAR'] = cvar
        results_df.loc[fund, 'Final Cumulative Returns'] = Cum_returns_final
        results_df.loc[fund, 'Max Drawdown'] = max_dd
        results_df.loc[fund, 'Omega Ratio'] = omega
        results_df.loc[fund, 'Sortino Ratio'] = sortino
        results_df.loc[fund, 'Stability of Timeseries'] = stability
        results_df.loc[fund, 'Tail Ratio'] = tail
        results_df.loc[fund, 'VaR'] = var
    # 添加 period 和 winlen 列，并填充对应的值
    results_df.insert(0, 'period', period)
    return results_df

def empyrical_metric_rolling(df, winlen, benchmark, period):
    """
        计算并返回其他金融量化指标。
        指标包括:
        simple_returns: 简单收益
        aggregate_returns_monthly: 月度聚合收益
        aggregate_returns_yearly: 年度聚合收益
        Cum_returns: 累积收益
        Rroll_annual_volatility: 滚动年化波动率
        Roll_max_drawdown: 滚动最大回撤
        Roll_sharpe_ratio: 滚动夏普比率
        Roll_sortino_ratio: 滚动索提诺比率
        Roll_up_capture: 滚动上行捕获
        alpha, beta: Alpha 和 Beta
        capture_ratio: 捕获比率
        Down_alpha_beta: 下行 Alpha 和 Beta
        Down_capture: 下行捕获
        Excess_sharpe: 超额夏普比率
        Roll_alpha_beta: 滚动 Alpha 和 Beta
        Roll_down_capture: 滚动下行捕获
        Up_alpha_beta: 上行 Alpha 和 Beta

    :param df, DataFrame: 基金收益率数据。
           winlen,int: 用于滚动指标计算的窗口大小。
           benchmark,pd.Series: 因子基准收益率,默认为None。
    :return: results_df, DataFrame:包含有窗长，因子基准收益率等对应基金的其他指标值。
    """
    # 计算今年以来收益率
    if period == 'Y':
        freq_y = 1
    elif period == 'Q':
        freq_y = 4  # 季频数据
        freq_q = 1
    elif period == 'M':
        freq_y = 12  # 月频数据
        freq_q = 4
        freq_m = 1
    elif period == 'D':
        freq_y = 252  # 日频数据
        freq_q = 120
        freq_m = 30
        freq_d = 1

    # 创建一个新的DataFrame来存储结果
    results_df = pd.DataFrame()
    # 对于每个基金，计算量化指标
    for fund in df.iloc[:, :-1].columns:
        returns = df[fund]

        # 计算各种量化指标
        Simple_returns = em.simple_returns(returns)  # 计算简单收益
        aggregate_returns_monthly = em.aggregate_returns(returns, 'monthly')  # 计算月度聚合收益
        aggregate_returns_yearly = em.aggregate_returns(returns, 'yearly')  # 计算年度聚合收益
        Cum_returns = em.cum_returns(returns)  # 计算累积收益

        Rroll_annual_volatility = em.roll_annual_volatility(returns, window=winlen)  # 计算滚动年化波动率
        Roll_max_drawdown = em.roll_max_drawdown(returns, window=winlen)  # 计算滚动最大回撤
        Roll_sharpe_ratio = em.roll_sharpe_ratio(returns, window=winlen)  # 计算滚动夏普比率
        Roll_sortino_ratio = em.roll_sortino_ratio(returns, window=winlen)  # 计算滚动索提诺比率

        # 如果未赋值benchmark，则就默认为空值，跳过一下函数调用
        if benchmark is not None:
            benchmark_series = pd.Series(benchmark).reindex(returns.index)
            returns = pd.Series(returns)

            capture_ratio = em.capture(returns, benchmark_series)  # 计算捕获比率
            Down_alpha_beta = em.down_alpha_beta(returns, benchmark_series)  # 计算下行alpha和beta
            Down_capture = em.down_capture(returns, benchmark_series)  # 计算下行捕获

            Roll_up_capture_yearly = em.roll_down_capture(returns, benchmark_series, window=freq_y)  # 计算年度滚动下行捕获
            Roll_down_capture_yearly = em.roll_down_capture(returns, benchmark_series, window=freq_y)#计算年度滚动下行捕获

            Roll_up_capture_monthly = em.roll_down_capture(returns, benchmark_series, window=freq_m)  # 计算月度滚动下行捕获
            Roll_down_capture_monthly = em.roll_down_capture(returns, benchmark_series, window=freq_m)  # 计算月度滚动下行捕获


        else:

            capture_ratio = None
            Down_alpha_beta = None
            Down_capture = None
            Roll_up_capture_yearly = None
            Roll_up_capture_monthly = None
            Roll_down_capture_yearly = None
            Roll_down_capture_monthly = None

        # 将结果存储在新的DataFrame中
        results_df[fund] = [Simple_returns, aggregate_returns_monthly, aggregate_returns_yearly, Cum_returns,
                            capture_ratio, Down_alpha_beta, Down_capture,
                            Rroll_annual_volatility,
                            Roll_up_capture_yearly, Roll_up_capture_monthly,Roll_down_capture_yearly, Roll_down_capture_monthly,Roll_max_drawdown, Roll_sharpe_ratio, Roll_sortino_ratio,
                            ]

    # 设置结果DataFrame的列名
    results_df.index = ['Simple Returns', 'Aggregate Returns (Monthly)', 'Aggregate Returns (Yearly)','Cumulative Returns',
                        'Capture Ratio', 'downAlphaBeta', 'downCapture',
                        'rollAnnualVolatility',
                        'rollUpCapture(Yearly)', 'rollUpCapture (Monthly)','rollDownCapture(Yearly)', 'rollDownCapture (Monthly)','rollMaxDrawdown', 'rollSharpeRatio', 'rollSortinoRatio'
                        ]

    results_df = results_df.transpose()
    # 添加 period 和 winlen 列，并填充对应的值
    results_df.insert(0, 'period', period)
    results_df.insert(1, 'winlen', winlen)
    return results_df

# 将以上的全部函数汇总封装为em_api：

def empyrical_metric(df, benchmark, period, winlen):
    # 其中为方便浏览，没有因子和窗口的指标的计算结果保存在Sheet1，带有因子和窗口的指标Sheet2
    results_df = empyrical_metrics(df, period)
    # 计算带有因子和窗口的指标
    results_df_rolling = empyrical_metric_rolling(df, winlen, benchmark, period)
    print("em",results_df)
    return results_df,results_df_rolling

from pyfinance import TSeries
def pyfinance_metrics(df, benchmark):
    """
        计算并返回基本金融量化指标。

        指标包括:
        Alpha: Alpha
        Batting Avg: 击球平均值
        Beta: Beta
        Beta Adj: 调整后的Beta
        Information Ratio: 信息比率
        Modigliani Squared: Modigliani Squared
        R Squared: R平方
        Adjusted R Squared: 调整后的R平方
        Tracking Error: 跟踪误差
        Treynor Ratio: Treynor比率
        T Stat Alpha: T统计量Alpha
        T Stat Beta: T统计量Beta
        Up Capture: 上行捕获率
        Annualized Retrun: 年化收益率
        Cum Retrun: 累计收益率
        Annualized Standard Deviation: 年化标准差
        Downside Deviation: 下行标准差
        Sharpe Ratio Monthly: 月度夏普比率
        Sharpe Ratio Yearly: 年度夏普比率
        Max Drawdown: 最大回撤
        Calmar Ratio: 卡玛比率
        Sortino Ratio: Sortino比率
        Drawdown End: 回撤结束值
        Gain to Loss Ratio: 收益损失比率
        Geometric Mean: 几何平均值
        Growth of X: X的增长
        Percent Negative: 负面百分比
        Percent Positive: 正面百分比
        Recovery Date: 恢复日期
        Ulcer Index: Ulcer指数
    :param price_tb, DataFrame: 基金收益率数据。
           benchmark (TSeries, optional): 用作基准的金融指标时间序列，例如，S&P 500或者道琼斯工业平均指数,默认为None。
    :return: results_df, DataFrame:包含仅需基金净收益数据对应基金的基本指标值。

    """
    # 创建一个新的DataFrame，用于存储每个基金的金融指标
    results_df = pd.DataFrame(index=df.iloc[:, :-1].columns, columns=[
        'Annualized Retrun', 'Cum Retrun', 'Annualized Standard Deviation', 'Downside Deviation',
        'Sharpe Ratio Monthly', 'Sharpe Ratio Yearly', 'Max Drawdown', 'Calmar Ratio', 'Sortino Ratio', 'Alpha',
        'Batting Avg', 'Beta', 'Beta Adj', 'Drawdown End',  'Gain to Loss Ratio', 'Geometric Mean',
        'Growth of X', 'Information Ratio', 'Modigliani Squared', 'Percent Negative', 'Percent Positive',
        'Recovery Date', 'R Squared', 'Adjusted R Squared', 'Sortino Ratio', 'Tracking Error', 'Treynor Ratio',
        'T Stat Alpha', 'T Stat Beta', 'Ulcer Index', 'Up Capture', 'CAPM'
    ])
    # 对每个基金进行循环
    for fund in df.iloc[:, :-1].columns:
        # 获取基金的收益率
        returns = df[fund]
        returns = pd.Series(returns)
        returns_yearly = returns

        # 将临时的收益率Series的频率调整为年度
        returns_yearly = returns_yearly.resample('Y').mean()
        # 将收益率Series的频率调整为月度
        returns_monthly = returns.resample('M').mean()

        returns = returns.resample('D').mean()
        # 创建一个TSeries对象，用于计算正常频率金融指标
        tseries = TSeries(returns)
        # 创建一个TSeries对象，用于计算月度金融指标
        tseries_month = TSeries(returns_monthly)
        # 创建一个年度的TSeries对象，用于计算年度金融指标
        tseries_year = TSeries(returns_yearly)

        # 计算并存储年化收益率
        results_df.loc[fund, 'Annualized Retrun'] = tseries.anlzd_ret()
        # 计算并存储累计收益率
        results_df.loc[fund, 'Cum Retrun'] = tseries.cuml_ret()
        # 计算并存储年化标准差
        results_df.loc[fund, 'Annualized Standard Deviation'] = tseries.anlzd_stdev()
        # 计算并存储下行标准差
        results_df.loc[fund, 'Downside Deviation'] = tseries.semi_stdev()
        # 计算并存储月度夏普比率
        results_df.loc[fund, 'Sharpe Ratio Monthly'] = tseries.sharpe_ratio()

        # 计算并存储年度夏普比率
        if len(tseries_year) < 3:
            results_df.loc[fund, 'Sharpe Ratio Yearly'] = 0
        else:
            results_df.loc[fund, 'Sharpe Ratio Yearly'] = tseries_year.sharpe_ratio()

        results_df.loc[fund, 'Max Drawdown'] = tseries.max_drawdown()  # 计算并存储最大回撤
        results_df.loc[fund, 'Calmar Ratio'] = tseries.calmar_ratio()  # 计算并存储卡玛比率
        results_df.loc[fund, 'Sortino Ratio'] = tseries.sortino_ratio()  # 计算Sortino比率
        results_df.loc[fund, 'Drawdown End'] = tseries.drawdown_end()  # 计算回撤结束值
        results_df.loc[fund, 'Gain to Loss Ratio'] = tseries.gain_to_loss_ratio()  # 计算收益损失比率
        results_df.loc[fund, 'Geometric Mean'] = tseries.geomean()  # 计算几何平均值
        results_df.loc[fund, 'Growth of X'] = tseries.growth_of_x()  # 计算X的增长
        results_df.loc[fund, 'Percent Negative'] = tseries.pct_negative()  # 计算负面百分比
        results_df.loc[fund, 'Percent Positive'] = tseries.pct_positive()  # 计算正面百分比
        results_df.loc[fund, 'Recovery Date'] = tseries.recov_date()  # 计算恢复日期
        results_df.loc[fund, 'Sortino Ratio'] = tseries.sortino_ratio()  # 计算Sortino比率
        results_df.loc[fund, 'Ulcer Index'] = tseries.ulcer_idx()  # 计算Ulcer指数

        if benchmark is not None:
            benchmark_series = TSeries(benchmark).reindex(returns.index)

            results_df.loc[fund, 'Batting Avg'] = tseries.batting_avg(benchmark_series) # 计算击球平均值
            results_df.loc[fund, 'Information Ratio'] = tseries.info_ratio(benchmark_series) # 计算信息比率
            results_df.loc[fund, 'Modigliani Squared'] = tseries.msquared(benchmark_series)  # 计算Modigliani Squared
            results_df.loc[fund, 'Tracking Error'] = tseries.tracking_error(benchmark_series)   # 计算跟踪误差
            results_df.loc[fund, 'Up Capture'] = tseries.up_capture(benchmark_series)  # 计算上行捕获率
            try:
                results_df.loc[fund, 'R Squared'] = tseries.rsq(benchmark_series)  # 计算R平方
                results_df.loc[fund, 'Adjusted R Squared'] = tseries.rsq_adj(benchmark_series)  # 计算调整后的R平方
                results_df.loc[fund, 'Treynor Ratio'] = tseries.treynor_ratio(benchmark_series)  # 计算Treynor比率
                results_df.loc[fund, 'T Stat Alpha'] = tseries.tstat_alpha(benchmark_series)  # 计算T统计量Alpha
                results_df.loc[fund, 'T Stat Beta'] = tseries.tstat_beta(benchmark_series)  # 计算T统计量Beta
            except Exception as e:
                print(f"计算指标时出错：{e}")

        else:
            results_df.loc[
                fund, ['Batting Avg', 'Information Ratio', 'Modigliani Squared', 'R Squared', 'Adjusted R Squared',
                       'Tracking Error', 'Treynor Ratio', 'T Stat Alpha', 'T Stat Beta', 'Up Capture']] = None
    for key, value in benchmark.items():
        results_df[key] = value

    # 返回包含基本金融指标的DataFrame
    return results_df

def pyfinance_metrics_rolling(df, benchmark):
    """
       计算并返回其他金融量化指标。
       指标包括:
       Down_Capture: 下行捕获率
       Downmarket_Filter: 下行市场过滤器
       Excess_Drawdown_Idx: 超额回撤指数
       Excess_Return: 超额回报
       Upmarket_Filter: 上行市场过滤器
       Cumulative_Index: 累积指数
       Drawdown_Index: 回撤指数
       Return_Index: 回报指数
       Relative_Return: 相对回报
       Rollup: 月度滚动统计量

   :param price_tb, DataFrame: 基金收益率数据。
          benchmark,pd.Series: 基准收益率,默认为None。
   :return: results_df, DataFrame:包含有基准收益率等对应基金的其他指标值。
       """
    # 创建一个新的DataFrame来存储结果
    results_df = pd.DataFrame()

    # 对于每个基金，计算量化指标
    for fund in df.iloc[:, :-1].columns:
        # 获取基金的收益率
        returns = df[fund]
        returns = pd.Series(returns)

        # 将临时的收益率Series的频率调整为年度
        returns_yearly = returns.resample('Y').mean()
        # 将收益率Series的频率调整为月度
        returns_monthly = returns.resample('M').mean()
        # 创建一个TSeries对象，用于计算正常频率金融指标
        tseries = TSeries(returns_monthly)
        # 创建一个年度的TSeries年度对象，用于计算年度金融指标
        tseries_year = TSeries(returns_yearly)

        # 如果benchmark不为空，则对其进行处理
        if benchmark is not None:
            benchmark_series = TSeries(benchmark).reindex(returns.index)
            benchmark_series = benchmark_series.resample('M').mean()

            # 计算下行捕获率等其他指标
            Down_Capture = tseries.down_capture(benchmark_series)  # 计算下行捕获率
            Downmarket_Filter = tseries.downmarket_filter(benchmark_series)  # 计算下行市场过滤器
            Excess_Drawdown_Idx = tseries.excess_drawdown_idx(benchmark_series)  # 计算超额回撤指数
            Excess_Return = tseries.excess_ret(benchmark_series)  # 计算超额回报
            Upmarket_Filter = tseries.upmarket_filter(benchmark_series)  # 计算上行市场过滤器
        else:
            Down_Capture, Downmarket_Filter, Excess_Drawdown_Idx, Excess_Return, Upmarket_Filter = None, None, None, None, None

        # 计算其他量化指标
        Cumulative_Index = tseries.cuml_idx()  # 计算累积指数
        Drawdown_Index = tseries.drawdown_idx()  # 计算回撤指数
        Return_Index = tseries.ret_idx()  # 计算回报指数
        Relative_Return = tseries.ret_rels()  # 计算相对回报
        Rollup_month = tseries.rollup('M')  # 计算月度滚动统计量，这里设置的频率是月度

        # 将结果存储在新的DataFrame中
        results_df[fund] = [pd.DataFrame(Cumulative_Index), Down_Capture, pd.DataFrame(Downmarket_Filter),
                            pd.DataFrame(Drawdown_Index), pd.DataFrame(Excess_Drawdown_Idx),
                            pd.DataFrame(Excess_Return), pd.DataFrame(Return_Index),
                            pd.DataFrame(Relative_Return), pd.DataFrame(Rollup_month), Upmarket_Filter]

    # 设置结果DataFrame的列名
    results_df.index = ['Cumulative_Index', 'Down_Capture', 'Downmarket_Filter', 'Drawdown_Index',
                        'Excess_Drawdown_Idx', 'Excess_Return', 'Return_Index', 'Relative_Return', 'Rollup_month',
                        'Upmarket_Filter']

    results_df = results_df.transpose()
    for key, value in benchmark.items():
        results_df[key] = value
    # 返回包含其他金融指标的DataFrame
    return results_df

# 将以上的全部函数汇总封装为pyf_api：
def pyfinance_metric(df, benchmark):
    # 以下是调用数据，计算并保存结果，其中为方便浏览，基础指标的计算结果保存在Sheet1，其他指标Sheet2
    # 计算基础金融指标
    results_df = pyfinance_metrics(df, benchmark)
    # 计算其他金融指标
    results_df_other = pyfinance_metrics_rolling(df, benchmark)
    print("pyf",results_df)
    return results_df,results_df_other

import alphalens as al


def alphalens_reloaded_metric(price_tb, factor_tb, subportfolio_num=5, ic_lag=[1, 2, 3], avgretplot=(5, 15), long_short=True,
                         group_neutral=False):
    #先3.8环境测试，然后贴过来
    return

def pyfolio_metric(price_tb, factor_tb, subportfolio_num=5, ic_lag=[1, 2, 3], avgretplot=(5, 15), long_short=True,
                         group_neutral=False):
    #函数命名ffn_plot,html,metric
    return

def alphalens_metric(price_tb,factor_tb,subportfolio_num=5,ic_lag=[1, 2, 3],avgretplot=(5, 15),long_short=True, group_neutral=False):
    '''
    返回各种绩效统计信息的字典。
    指标包括：
        returns：收益率数据表。
        alpha_beta：Alpha和Beta数据表。
        mean_quant_ret：分位数平均收益率数据表。
        std_quantile：分位数标准差数据表。
        mean_quant_ret_bydate：按日期的分位数平均收益率数据表。
        std_quant_daily：每日分位数标准差数据表。
        mean_quant_rateret_bydate：按日期的分位数收益率变化率数据表。
        compstd_quant_daily：标准差转换后的每日分位数数据表。
        ic：信息系数数据表。
        quantile_turnover：分位数换手率数据表。
        autocorrelation：自相关系数数据表。
        avg_cumulative_returns：平均累积收益率数据表。
        mean_ret_spread_quant：分位数收益率差异平均值数据表。
        std_spread_quant：分位数收益率差异标准差数据表。
        quant_turnover：分位数换手率数据表。
        autocorr：自相关系数数据表。
        average_cumulative_ret：平均累积收益率数据表。

    :param price_tb, DataFrame: 价格数据表。
    :param factor_tb, DataFrame: 因子数据表。
    :param subportfolio_num, int, optional: 子投资组合数量。默认为5。
    :param ic_lag, list of int, optional: IC滞后期列表。默认为[1, 2, 3]。
    :param avgretplot, tuple of int, optional: 平均收益率绘图参数。默认为(5, 15)。
    :param long_short, bool, optional: 是否为多空组合。默认为True。
    :param group_neutral, bool, optional: 是否为组合中性。默认为False。

    :return: dict, 包含各种绩效统计信息的字典，每个键对应一个 DataFrame。
    '''
    price_tb.index.name = 'Date'
    # 给列索引命名
    price_tb.columns.name = 'assets'
    factor_tb.index = pd.to_datetime(factor_tb.index)
    price_tb.index = pd.to_datetime(price_tb.index)
    results = {}

    #---------------转换数据格式------------------------------------

    # 使用 set_index 函数将原来的索引列设为一级索引
    restructured_factor_tb = factor_tb.set_index(factor_tb.index)
    # 使用 stack 函数将列索引股票代码转换为第二重索引
    restructured_factor_tb = restructured_factor_tb.stack()
    # 重命名索引
    restructured_factor_tb.index.names = ['Date', 'assets']
    price_tb = price_tb.shift(-1)
    periods = tuple(ic_lag)

    # ---------------绩效回测------------------------------------
    #因子分析
    factor_data = al.utils.get_clean_factor_and_forward_returns(restructured_factor_tb,price_tb,quantiles = subportfolio_num,periods = periods,max_loss=0.35)
    #收益率分析
    returns_byasset = price_tb.pct_change()
    returns = al.performance.factor_returns(factor_data,demeaned=True,group_adjust=False,equal_weight=False,by_asset=False)
    alpha_beta = al.performance.factor_alpha_beta(factor_data,returns=returns,demeaned=True,group_adjust=False,equal_weight=False)
    mean_quant_ret, std_quantile = al.performance.mean_return_by_quantile(factor_data,by_group=False,demeaned=long_short,group_adjust=group_neutral,)
    mean_quant_ret_bydate, std_quant_daily = al.performance.mean_return_by_quantile(factor_data,by_date=True,by_group=False,demeaned=long_short,group_adjust=group_neutral,)
    mean_quant_rateret_bydate = mean_quant_ret_bydate.apply(al.utils.rate_of_return,axis=0,base_period=mean_quant_ret_bydate.columns[0],)
    compstd_quant_daily = std_quant_daily.apply(al.utils.std_conversion, axis=0, base_period=std_quant_daily.columns[0])
    #信息分析
    ic = al.performance.factor_information_coefficient(factor_data, group_adjust=False, by_group=False)
    # 换手率分析
    quantile_factor = factor_data["factor_quantile"]
    quantile_turnover = {p: pd.concat([al.performance.quantile_turnover(quantile_factor, q, p)for q in range(1, int(quantile_factor.max()) + 1)],axis=1,)for p in periods}
    autocorrelation = pd.concat([al.performance.factor_rank_autocorrelation(factor_data, period)for period in periods],axis=1,)

    before, after = avgretplot
    mean_ret_spread_quant, std_spread_quant = al.performance.compute_mean_returns_spread(mean_quant_rateret_bydate,factor_data["factor_quantile"].max(),factor_data["factor_quantile"].min(),std_err=compstd_quant_daily,)
    quant_turnover = al.performance.quantile_turnover(factor_data['factor_quantile'], quantile = subportfolio_num, period=1)
    autocorr = al.performance.factor_rank_autocorrelation(factor_data, period=1)
    average_cumulative_ret = al.performance.average_cumulative_return_by_quantile(factor_data,returns_byasset,periods_before=before,periods_after=after,demeaned=True,group_adjust=False,by_group=False)

    results['returns'] = returns
    results['alpha_beta'] = alpha_beta
    results['mean_quant_ret'] = mean_quant_ret
    results['std_quantile'] = std_quantile
    results['mean_quant_ret_bydate'] = mean_quant_ret_bydate
    results['std_quant_daily'] = std_quant_daily
    results['mean_quant_rateret_bydate'] = mean_quant_rateret_bydate
    results['compstd_quant_daily'] = compstd_quant_daily
    results['ic'] = ic
    results['quantile_turnover'] = quantile_turnover
    results['autocorrelation'] = autocorrelation
    results['mean_ret_spread_quant'] = mean_ret_spread_quant
    results['std_spread_quant'] = std_spread_quant
    results['quant_turnover'] = quant_turnover
    results['autocorr'] = autocorr
    results['average_cumulative_ret'] = average_cumulative_ret

    return results
