import pandas as pd
import numpy as np
import copy
from scipy.stats import spearmanr, pearsonr
from cal_metric_model import ffn_metric,quantstats_metric,empyrical_metric,pyfinance_metric,alphalens_metric

def portfolio_by_ret(ret_tb, subportfolio_num):
    """
    根据收益率构建投资组合

    参数:
    ret_tb: DataFrame, 收益率数据表，交易日期，列为标的名称
    subportfolio_num: int, 子投资组合的数量

    返回值:
    portfolio_tb: DataFrame, 投资组合数据表
    """
    portfolio_tb = pd.DataFrame(index=ret_tb.index)
    portfolio_tb['total'] = ret_tb.mean(axis=1)
    for date, row in ret_tb.iterrows():
        sorted_factor = row.sort_values(ascending=False, kind='mergesort')
        group_size = len(sorted_factor) // subportfolio_num
        for i in range(subportfolio_num):
            if i == subportfolio_num - 1:  # 如果是最后一组
                group_factor = sorted_factor[i * group_size:]  # 将剩余的基金都放在最后一组
            else:
                group_factor = sorted_factor[i * group_size:(i + 1) * group_size]
            portfolio_tb.loc[date, f'group_{i + 1}'] = group_factor.mean()
    portfolio_tb['long_short'] = portfolio_tb['group_1'] - portfolio_tb[f'group_{subportfolio_num}']
    return portfolio_tb

def calculate_ic(factor_tb, ret_tb,subportfolio_num):
    """
    计算全样本的IC和分组IC

    参数:
    factor_tb: DataFrame, 因子数据表，交易日期，列为标的名称
    ret_tb: DataFrame, 收益率数据表，交易日期，列为标的名称
    subportfolio_num: int, 子投资组合的数量

    返回值:
    rank_ic_tb: DataFrame, rank_ic数据表
    normal_ic_tb: DataFrame, normal_ic数据表
    """
    rank_ic_tb = pd.DataFrame(index=factor_tb.index)
    normal_ic_tb = pd.DataFrame(index=factor_tb.index)

    # 计算全样本的IC
    for date in factor_tb.index:
        factor_values = factor_tb.loc[date]
        returns = ret_tb.shift(-1).loc[date]
        valid_data = pd.concat([factor_values, returns], axis=1)
        valid_data = valid_data.replace([np.inf, -np.inf], np.nan).dropna()
        if len(valid_data) < 2:
            continue
        factor_values, returns = valid_data.iloc[:, 0], valid_data.iloc[:, 1]
        rank_ic = spearmanr(factor_values, returns)[0]
        normal_ic = pearsonr(factor_values, returns)[0]
        rank_ic_tb.loc[date, 'total'] = rank_ic
        normal_ic_tb.loc[date, 'total'] = normal_ic

    '''
    rank_ic_tb['total'] = factor_tb.replace([np.inf, -np.inf], np.nan).apply(lambda x: spearmanr(x, ret_tb.replace([np.inf, -np.inf], np.nan).shift(-1).loc[x.name])[0], axis=1)
    normal_ic_tb['total'] = factor_tb.replace([np.inf, -np.inf], np.nan).apply(lambda x: pearsonr(x, ret_tb.replace([np.inf, -np.inf], np.nan).shift(-1).loc[x.name])[0], axis=1)
    '''

    # 分组计算IC
    for date, row in factor_tb.iterrows():
        sorted_factor = row.sort_values(ascending=False, kind='mergesort')
        group_size = len(sorted_factor) // subportfolio_num
        for i in range(subportfolio_num):
            if i == subportfolio_num - 1:  # 如果是最后一组
                group_factor = sorted_factor[i * group_size:]  # 将剩余的基金都放在最后一组
            else:
                group_factor = sorted_factor[i * group_size:(i + 1) * group_size]
            group_returns = ret_tb.shift(-1).loc[date, group_factor.index]
            valid_data = pd.concat([group_factor, group_returns], axis=1)
            valid_data = valid_data.replace([np.inf, -np.inf], np.nan).dropna()
            if len(valid_data) < 2:
                continue
            group_factor, group_returns = valid_data.iloc[:, 0], valid_data.iloc[:, 1]
            rank_ic = spearmanr(group_factor, group_returns)[0]
            normal_ic = pearsonr(group_factor, group_returns)[0]
            rank_ic_tb.loc[date, f'rank_ic_{i + 1}'] = rank_ic
            normal_ic_tb.loc[date, f'normal_ic_{i + 1}'] = normal_ic
    return rank_ic_tb, normal_ic_tb

def calculate_ic_lag(factor_tb, ret_tb,lag):
    """
    计算滞后期IC

    参数:
    factor_tb: DataFrame, 因子数据表，交易日期，列为标的名称
    ret_tb: DataFrame, 收益率数据表，交易日期，列为标的名称
    lag: int, 滞后期数

    返回值:
    rank_ic_lag_df: DataFrame, 滞后的排名rank_ic数据表
    normal_ic_lag_df: DataFrame, 滞后的normal_ic数据表
    """
    rank_ic_lag_df = pd.DataFrame()
    normal_ic_lag_df = pd.DataFrame()
    for date, row in factor_tb.iterrows():
        # 对因子值排序，采用降序排序
        sorted_factor = row.sort_values(ascending=False, kind='mergesort')
        if date in ret_tb.index:
            for i in lag:
                # 获取滞后期的收益率
                returns = ret_tb.shift(-i).loc[date]
                valid_data = pd.concat([sorted_factor, returns], axis=1)
                valid_data = valid_data.replace([np.inf, -np.inf], np.nan).dropna()
                if len(valid_data) < 2:
                    continue
                factor, returns = valid_data.iloc[:, 0], valid_data.iloc[:, 1]
                rank_ic = spearmanr(factor, returns)[0]
                normal_ic = pearsonr(factor, returns)[0]
                rank_ic_lag_df.loc[date, f'rank_ic_{i}'] = rank_ic
                normal_ic_lag_df.loc[date, f'normal_ic_{i}'] = normal_ic
    return rank_ic_lag_df, normal_ic_lag_df

def calculate_ic_statistics(df):
    """
    计算IC的各类统计量

    参数:
    df: DataFrame, IC数据表

    返回值:
    df_cum: DataFrame, 累计IC数据表
    df_ma12: DataFrame, 12期移动平均IC数据表
    df_corr: DataFrame, IC的相关性数据表
    """
    df_cum = df.cumsum()
    df_ma12 = df.rolling(window=12).mean()
    df_corr = df.corr()
    return df_cum,df_ma12,df_corr

def calculate_ic_monthlymap(df):
    """
    计算IC的月度图

    参数:
    df: DataFrame, IC数据表

    返回值:
    monthlymap_analysis: DataFrame, IC的月度图数据表
    """
    df_copy = copy.deepcopy(df)
    df_copy['year'] = df_copy.index.year
    df_copy['month'] = df_copy.index.month
    if 'total' in df_copy.columns:
        monthlymap_analysis = df_copy.groupby(['year', 'month'])['total'].mean().unstack()
        monthlymap_analysis.columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                       'August', 'September', 'October', 'November', 'December']
    else:
        print("'total' column not found in the DataFrame.")
        monthlymap_analysis = None
    return monthlymap_analysis

def create_group_df(position_df, price_tb, subportfolio_num):
    """
    创建组别数据表

    参数:
    position_df: DataFrame, 持仓数据表，交易日期，列为标的名称
    price_tb: DataFrame, 价格数据表，交易日期，列为标的名称
    subportfolio_num: int, 子投资组合的数量

    返回值:
    group_df: DataFrame, 组别数据表
    """
    # 创建一个和 price_tb 结构相同的空 DataFrame，命名为 group_df
    group_df = pd.DataFrame(index=price_tb.index, columns=price_tb.columns)
    group_size = len(position_df.columns) // subportfolio_num
    # 如果 group_size 不为整数，则取大于它的最近整数
    if len(position_df.columns) % subportfolio_num != 0:
        group_size = group_size + 1
    # 使用 np.repeat 和 np.arange 创建一个数组，表示每个基金的组别
    groups = np.repeat(np.arange(1, subportfolio_num + 1), group_size)
    # 如果基金数量不能被 subportfolio_num 整除，那么最后一组的基金数量可能会少于 group_size,将多余的基金都归入最后一组
    groups = groups[:len(position_df.columns)]
    groups[-(len(position_df.columns) % group_size):] = subportfolio_num
    # 使用向量化操作设置 group_df 的值
    group_df[:] = np.tile(groups, (len(group_df), 1))
    # 如果 position_df 的值为空，则将对应的 group_df 的值设置为 0
    group_df[position_df.isna()] = 0
    return group_df

def cal_turnoverRate(position_df, price_tb, group_df, subportfolio_num):
    """
    计算换手率

    参数:
    position_df: DataFrame, 持仓数据表，交易日期，列为标的名称
    price_tb: DataFrame, 价格数据表，交易日期，列为标的名称
    group_df: DataFrame, 组别数据表，交易日期，列为标的名称
    subportfolio_num: int, 子投资组合的数量

    返回值:
    turnover_tb: DataFrame, 换手率数据表
    """
    turnover_tb = pd.DataFrame(index=position_df.index, columns=['total_turnover_rate'] + [f'group_{i}_turnover_rate' for i in range(1, subportfolio_num + 1)])
    for date_idx in range(1, len(position_df.index)):
        date = position_df.index[date_idx]
        prev_date = position_df.index[date_idx - 1]
        if date in price_tb.index and prev_date in price_tb.index:
            changed_stocks = group_df.loc[date] != group_df.loc[prev_date]
            turnover_value = price_tb.loc[date, changed_stocks].sum()
            total_value = price_tb.loc[date].sum()
            total_turnover_rate = turnover_value / total_value if total_value != 0 else 0
            turnover_tb.loc[date, 'total_turnover_rate'] = total_turnover_rate
            for group in range(1, subportfolio_num + 1):
                group_changed_stocks = (group_df.loc[date] == group) & (group_df.loc[prev_date] == group)
                group_turnover_value = price_tb.loc[date, group_changed_stocks].sum()
                group_total_value = price_tb.loc[date, group_changed_stocks].sum()
                group_turnover_rate = group_turnover_value / group_total_value if group_total_value != 0 else 0
                turnover_tb.loc[date, f'group_{group}_turnover_rate'] = group_turnover_rate
    return turnover_tb


def cal_netValue_statistics(nav_tb, period):
    """
        计算并返回基本金融量化指标。
        指标包括:
        最新（%）
        近1月（%）
        近3月（%）
        近1年（%）
        近3年（%）
        近5年（%）
        成立以来（%）
        25%分位点
        50%分位点
        75%分位点
        最小值
        最大值
    :param df, DataFrame: 收益率(returns_tb)数据。
    :return: results_df, DataFrame:包含仅需基金净收益数据对应基金的基本指标值
    """
    # 计算最新收益率
    latest_returns = nav_tb.iloc[-1] * 100
    # 计算今年以来收益率
    if period == 'Y':
        freq = 1
    elif period == 'Q':
        freq = 4  # 季频数据
    elif period == 'M':
        freq = 12  # 月频数据
    else:
        freq = 252  # 日频数据

    recent_1_year_returns = nav_tb.rolling(window=freq).sum().iloc[-1] * 100
    recent_3_year_returns = nav_tb.rolling(window=3 * freq).sum().iloc[-1] * 100
    recent_5_year_returns = nav_tb.rolling(window=5 * freq).sum().iloc[-1] * 100
    since_inception_returns = nav_tb.sum() * 100

    # 计算近1月、近3月、近1年、近3年、近5年、成立以来收益率
    if period == 'D':
        recent_1_month_returns = nav_tb.rolling(window=30).sum().iloc[-1] * 100
        recent_3_month_returns = nav_tb.rolling(window=30 * 3).sum().iloc[-1] * 100
    elif period == 'M':
        recent_1_month_returns = nav_tb.iloc[-1] * 100
        recent_3_month_returns = nav_tb.rolling(window=3).sum().iloc[-1] * 100
    else:
        recent_1_month_returns = None
        recent_3_month_returns = None

    # 计算分位点
    quantiles = nav_tb.quantile([0.25, 0.5, 0.75])
    min_returns = nav_tb.min()
    max_returns = nav_tb.max()

    # 构建统计指标表
    stats_tb = pd.DataFrame({
        '最新（%）': latest_returns,
        '近1月（%）': recent_1_month_returns,
        '近3月（%）': recent_3_month_returns,
        '近1年（%）': recent_1_year_returns,
        '近3年（%）': recent_3_year_returns,
        '近5年（%）': recent_5_year_returns,
        '成立以来（%）': since_inception_returns,
        '25%分位点': quantiles.loc[0.25],
        '50%分位点': quantiles.loc[0.5],
        '75%分位点': quantiles.loc[0.75],
        '最小值': min_returns,
        '最大值': max_returns,
    })

    return stats_tb

def cal_performance(ret_tb, benchmark, period, winlen):
    ret_tb_copy = copy.deepcopy(ret_tb)
    ret_tb_copy['year'] = ret_tb_copy.index.year
    ffn_performance = {}
    empyrical_performance = {}
    empyrical_performance_with_factors = {}
    qs_performance = {}
    pyf_performance = {}
    pyf_performance_other = {}
    # 按年份分组计算绩效
    for year, data in ret_tb_copy.groupby('year'):
        # 检查收益率的长度是否大于1
        if len(data) > 1:
            # 调用计算绩效的函数
            ffn_perf = ffn_metric(data)
            qs_perf = quantstats_metric(data)
            empyrical_perf, empyrical_perf_with_factors = empyrical_metric(data, benchmark, period, winlen)
            pyf_perf, pyf_perf_other = pyfinance_metric(data, benchmark)
            # 将每个绩效包的年度绩效数据存储到对应的字典中
            ffn_performance[str(year)] = ffn_perf
            empyrical_performance[str(year)] = empyrical_perf
            empyrical_performance_with_factors[str(year)] = empyrical_perf_with_factors
            qs_performance[str(year)] = qs_perf
            pyf_performance[str(year)] = pyf_perf
            pyf_performance_other[str(year)] = pyf_perf_other
        else:
            print(f"{year} 年仅有一条数据不能计算指标")

    # 计算全部时间区间的数据
    ffn_perf_alltime = ffn_metric(ret_tb)
    qs_perf_alltime = quantstats_metric(ret_tb)
    empyrical_perf_alltime, empyrical_perf_with_factors_alltime = empyrical_metric(ret_tb, benchmark, period, winlen)
    pyf_perf_alltime, pyf_perf_other_alltime = pyfinance_metric(ret_tb, benchmark)
    # 将全部时间区间的绩效数据存储到对应的字典中
    ffn_performance["alltime"] = ffn_perf_alltime
    empyrical_performance["alltime"] = empyrical_perf_alltime
    empyrical_performance_with_factors["alltime"] = empyrical_perf_with_factors_alltime
    qs_performance["alltime"] = qs_perf_alltime
    pyf_performance["alltime"] = pyf_perf_alltime
    pyf_performance_other["alltime"] = pyf_perf_other_alltime

    return ffn_performance, empyrical_performance, empyrical_performance_with_factors, qs_performance, pyf_performance, pyf_performance_other

def cal_portfolio_metric(price_tb_original, ret_tb, factor_tb, position_tb,benchmark,subportfolio_num,IC_lag_n,period, winlen,avgretplot=(5, 15)):
    """
    计算投资组合指标

    参数:
    price_tb_original: DataFrame, 原始价格数据表，交易日期，列为标的名称
    ret_tb: DataFrame, 收益率数据表，交易日期，列为标的名称
    factor_tb: DataFrame, 因子数据表，交易日期，列为标的名称
    position_tb: DataFrame, 持仓数据表，交易日期，列为标的名称
    benchmark: str, 基准
    subportfolio_num: int, 子投资组合的数量
    IC_lag_n: int, IC滞后期数
    period: str, 期间
    winlen: int, 窗口长度

    返回值:
    cal_metric_results: dict, 包含投资组合指标的字典
    """
    nav_tb = (1 + ret_tb.fillna(0)).cumprod()
    portfolio_tb = portfolio_by_ret(ret_tb,subportfolio_num)
    rank_ic ,normal_ic = calculate_ic(factor_tb, ret_tb,subportfolio_num)
    rank_ic_lag, normal_ic_lag = calculate_ic_lag(factor_tb, ret_tb, IC_lag_n)

    #计算rank_ic类指标
    rank_ic_cum, rank_ic_ma12,rank_ic_cor  = calculate_ic_statistics(rank_ic)
    rank_ic_monthlymap = calculate_ic_monthlymap(rank_ic)

    #计算normal_ic类指标
    normal_ic_cum,normal_ic_ma12,normal_ic_cor = calculate_ic_statistics(normal_ic)
    normal_ic_monthlymap = calculate_ic_monthlymap(normal_ic)

    #计算换手率
    group_tb = create_group_df(position_tb, price_tb_original,subportfolio_num)
    turnover_tb = cal_turnoverRate(position_tb, price_tb_original, group_tb, subportfolio_num)
    stats_tb = cal_netValue_statistics(nav_tb, period)
    if not portfolio_tb.isna().all().all():
        ffn_performance, empyrical_performance, empyrical_performance_with_factors, qs_performance, pyf_performance, pyf_performance_other = cal_performance(portfolio_tb, benchmark, period, winlen)
        alphalens_perf = None
        try:
            from alphalens.utils import MaxLossExceededError
            alphalens_perf = alphalens_metric(price_tb_original, factor_tb, subportfolio_num, IC_lag_n, avgretplot,long_short=True, group_neutral=False)
        except MaxLossExceededError as e:
            # 捕获异常并将错误信息打印出来
            print(e)
    else:
        ffn_performance = empyrical_performance = empyrical_performance_with_factors = qs_performance = pyf_performance = pyf_performance_other = None
        alphalens_perf = None
    cal_metric_results = {
        'portfolio_tb': portfolio_tb,
        'ret_tb':ret_tb,
        'nav_tb': nav_tb,
        'rank_ic':rank_ic,
        'rank_ic_lag': rank_ic_lag,
        'normal_ic_lag': normal_ic_lag,
        'rank_ic_cum': rank_ic_cum,
        'rank_ic_ma12': rank_ic_ma12,
        'rank_ic_cor': rank_ic_cor,
        'rank_ic_monthlymap': rank_ic_monthlymap,
        'normal_ic': normal_ic,
        'normal_ic_cum': normal_ic_cum,
        'normal_ic_ma12': normal_ic_ma12,
        'normal_ic_cor': normal_ic_cor,
        'normal_ic_monthlymap': normal_ic_monthlymap,
        'turnover_tb': turnover_tb,
        'stats_tb': stats_tb,
        'ffn_performance': ffn_performance,
        'empyrical_performance': empyrical_performance,
        'empyrical_performance_rolling': empyrical_performance_with_factors,
        'qs_performance': qs_performance,
        'pyf_performance': pyf_performance,
        'pyf_performance_rolling': pyf_performance_other,
        'alphalens_perf': alphalens_perf
    }
    return cal_metric_results

