import os
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request,session
import pickle
import sys

def create_app(result,CONFIG=None):
    app = Flask(__name__)
    app.debug = True
    import secrets
    app.secret_key = secrets.token_hex(16)

    if 'performance_total' in result:
        merged_performance = result['performance_total']
        del result['performance_total']
    else:
        # 如果不存在 'performance_total' 键，则给出相应的处理方式
        merged_performance = result  # 或者进行其他适当的操作

    # 读取config中的参数
    FREQUENCY_INTERVAL = CONFIG["FREQUENCY_INTERVAL"]
    freq_position = CONFIG["freq_position"]
    benchmark = CONFIG["benchmark"]
    subportfolio_num = CONFIG["subportfolio_num"]
    IC_lag_n = CONFIG["IC_lag_n"]
    period = CONFIG["period"]
    winlen = CONFIG["winlen"]

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/show.html')
    def home2():
        return render_template('show.html',
                               FREQUENCY_INTERVAL=FREQUENCY_INTERVAL,
                               freq_position=freq_position,
                               benchmark=benchmark,
                               subportfolio_num=subportfolio_num,
                               IC_lag_n=IC_lag_n,
                               period=period,
                               winlen = winlen)

    def get_initial_path(dropdown_value, result):
        initial_path = '/'
        path_levels = 0
        current_result = result
        while isinstance(current_result, dict):
            print("Current Result:", current_result)
            if dropdown_value in current_result:
                initial_path += str(dropdown_value)
                path_levels += 1
                break
            else:
                initial_path += 'all/'
                path_levels += 1
                # 深入到下一层级
                current_result = next(iter(current_result.values()))
        print(initial_path)
        print('path_levels', path_levels)
        return initial_path, path_levels

    @app.route('/get_initial_path', methods=['POST'])
    def handle_initial_path():
        data = request.json
        dropdown_value = data['dropdownValue']
        initial_path, path_levels = get_initial_path(dropdown_value, result)
        session['initialPath'] = initial_path
        session['resultlenth'] = path_levels
        return jsonify({'initialPath': initial_path, 'pathLevels': path_levels})

    def find_common_suffix(elements):
        reversed_elements = [element[::-1] for element in elements]
        common_prefix = os.path.commonprefix(reversed_elements)
        return common_prefix[::-1]

    def filter_data(data, path, level,filtered_elements=None):
        print('filtered_elements', filtered_elements)
        print('path',path)
        if filtered_elements is None:
            filtered_elements = []
        if level < len(path):
            keys = [key.strip() for key in path[level].split(',')]
            print('未到筛选层级',keys,level)
            for key in keys:
                if key == 'all':
                    for k in list(data.keys()):
                        if isinstance(data[k], dict):
                            next_data = data.get(k, {})
                            data[k] = filter_data(next_data, path, level + 1, filtered_elements)
                elif key in data:
                    next_data = data.get(key, {})
                    if isinstance(next_data, dict):
                        data[key] = filter_data(next_data, path, level + 1, filtered_elements)
        else:
            for key in list(data.keys()):
                print('待检验因子',key)
                if key not in filtered_elements:
                    print('不符合因子', key)
                    del data[key]
        return data

    def remove_empty_dicts(data):
        keys_to_delete = []
        for key in data:
            if isinstance(data[key], dict):
                data[key] = remove_empty_dicts(data[key])
                if not data[key]:  # 如果值为空
                    keys_to_delete.append(key)
        for key in keys_to_delete:
            del data[key]
        return data


    @app.route('/filter_result', methods=['POST'])
    def handle_result():
        initial_path = str(session.get('initialPath'))  # 从 session 获取 initialPath
        print('initial_path',initial_path)
        filter_condition = request.json
        resultKeys = filter_condition['resultKeys']
        print('resultKeys',resultKeys)
        session['columnName'] = filter_condition['columnName']
        session['minValue'] = filter_condition['minValue']
        session['maxValue'] = filter_condition['maxValue']


        # 处理结果数据
        filtered_elements = [element[:element.index('signal') + len('signal')] if 'signal' in element else element for element in resultKeys]
        path_components = initial_path.strip('/').split('/')
        while path_components and path_components[-1] == '':
            path_components.pop()
        path = path_components[:-2]
        filter_result = filter_data(result, path, 0, filtered_elements)
        filter_result = remove_empty_dicts(filter_result)
        print('符合因子', filter_result)

        return jsonify({'message': 'Result received'})

    def transform_data(title_pre, data, datasets):
        for name, df in data.items():
            if len(df.index) > 50:
                indices = np.linspace(0, len(df.index) - 1, 50, dtype=int)  # 均匀取50个索引
            df.index = pd.to_datetime(df.index)
            labels = df.index.strftime('%Y-%m-%d').tolist()
            labels = [labels[i] for i in indices]  # 使用这些索引取值
            if isinstance(df, pd.Series):
                df = df.to_frame(name)
            for column_name in df.columns:
                df[column_name] = df[column_name].fillna(0)
                values = [value for value in df[column_name]]
                values = [values[i] for i in indices]  # 使用这些索引取值
                datasets.append({
                    'title': title_pre + "_" + str(name),
                    'values': values,
                    'labels': labels,
                })
        return

    def transform_data_heatmap(title_pre, df):
        datasets = []
        y = [str(i) for i in list(df.index)]  # 添加y坐标
        x = list(df.columns)  # 添加x坐标
        for index, row in df.iterrows():
            values = row.fillna(0).tolist()
            datasets.append({
                'title': title_pre,
                'values': values,
                'x': x,  # 添加x坐标到结果中
                'y': y  # 添加y坐标到结果中
            })
        return datasets

    '''
        递归获取key
        返回list
    '''

    def get_combinations(data, path, level=0, res=None):
        if res is None:
            res = []
        if level < len(path):
            keys = [key.strip() for key in path[level].split(',')]
            for key in keys:
                if key == 'all':
                    for k in data.keys():
                        if isinstance(data[k], dict):
                            next_data = data.get(k, {})
                            res = get_combinations(next_data, path, level + 1, res)
                elif key in data:
                    next_data = data.get(key, {})
                    if isinstance(next_data, dict):
                        res = get_combinations(next_data, path, level + 1, res)
        else:
            res.extend(data.keys())
        return res

    '''
        递归获取key对应的data
        返回字典 key value（为df或其他）类型
        key的格式为所有层级组成的字符串
    '''

    def get_combinations_data(data, path, level=0, full_key='', last_key=None):
        res = {}
        if level < len(path):
            keys = [key.strip() for key in path[level].split(',')]
            for key in keys:
                if key == 'all':
                    for k in data.keys():
                        if isinstance(data[k], dict):
                            next_data = data.get(k, {})
                            new_key = f'{full_key}/{k}' if full_key else k
                            res.update(get_combinations_data(next_data, path, level + 1, new_key, key)[0])
                elif key in data:
                    next_data = data.get(key, {})
                    if isinstance(next_data, dict):
                        new_key = f'{full_key}/{key}' if full_key else key
                        res.update(get_combinations_data(next_data, path, level + 1, new_key, key)[0])
                    else:
                        new_key = f'{full_key}/{key}' if full_key else key
                        print(next_data)
                        res[new_key] = next_data  # 如果不是字典，添加键和对应的数据
        return res, last_key

    def get_keys_at_level(data, level, path=[]):
        if level == 0:
            keys = list(data.keys())
            keys.append('all')
            return keys
        else:
            all_keys = []
            all_keys = get_combinations(data, path, 0, all_keys)
            # 将字典的键转换为集合进行去重
            unique_keys = list(dict.fromkeys(all_keys))
            # 检查是否为空
            if unique_keys and 'portfolio_tb' not in unique_keys:
                # 如果不为空，添加 'all'
                unique_keys.append('all')
            # 转换回列表
            all_keys = list(unique_keys)
            print(all_keys)
            return list(all_keys)

    def get_option_type(key):
        if key in ['rank_ic_cor', 'normal_ic_cor', 'rank_ic_monthlymap', 'normal_ic_monthlymap']:
            return 'heatmap'
        if key in ['stats_tb']:
            return 'table'
        if key in ['ffn_performance', 'empyrical_performance', 'empyrical_performance_rolling','qs_performance', 'pyf_performance', 'pyf_performance_rolling','alphalens_perf']:
            return 'per_table'
        elif key in ['portfolio_tb', 'nav_tb','ret_tb', 'rank_ic', 'rank_ic_lag', 'normal_ic_lag', 'rank_ic_cum', 'rank_ic_ma12',
                     'normal_ic', 'normal_ic_cum', 'normal_ic_ma12', 'turnover_tb']:
            return 'linechart'
        return ''


    @app.route('/get_keys/<int:level>', defaults={'path': ''})
    @app.route('/get_keys/<int:level>/<path:path>')
    def get_keys(level, path):
        path = path.split('/') if path else []
        keys = get_keys_at_level(result, level, path)
        if isinstance(keys, pd.DataFrame):
            keys = keys.to_dict()
        return jsonify(keys=keys)

    '''
        调用函数进行data获取
    '''

    def filter_performance_tb(tb):
        # 如果 session['minValue'] 为空，则设为无穷小
        if session['minValue'] == '':
            min_value = sys.float_info.min
        else:
            min_value = float(session['minValue'])
        print(min_value)
        # 如果 session['maxValue'] 为空，则设为无穷大
        if session['maxValue'] == '' :
            max_value = sys.float_info.max
        else:
            max_value = float(session['maxValue'])

        column_name = session.get('columnName', '')
        if column_name and column_name in tb.columns:
            # 如果 column_name 是 'factorname'，则跳过后面的处理步骤
            if column_name == 'factorname':
                return tb
            # 移除百分号并除以100
            tb[column_name] = tb[column_name].str.rstrip('%').astype('float') / 100.0
            # 根据 min_value 和 max_value 进行筛选
            if min_value != sys.float_info.min and max_value != sys.float_info.max:
                tb = tb[(tb[column_name] >= min_value) & (tb[column_name] <= max_value)]
            elif min_value != sys.float_info.min:
                tb = tb[tb[column_name] >= min_value]
            elif max_value != sys.float_info.max:
                tb = tb[tb[column_name] <= max_value]
            # 将某一列数据转换为百分比形式
            tb[column_name] = (tb[column_name] * 100).astype(str) + '%'

            # 删除 'factorname' 列中不在 session['selected_factor'] 列表里面的因子名称所在行
        tb = tb[tb['factorname'].isin(session['selected_factor'])]
        return tb

    @app.route('/get_data/<path:path>')
    def get_data(path):
        path = path.split('/')
        data = result
        print("get_data is ok")
        last_key_data, last_key = get_combinations_data(data, path, 0, '')
        df_data = []
        option_type = get_option_type(path[-1])
        print('option_type',option_type)
        result_lenth = session['resultlenth']
        path_length = len(path)
        if option_type == '' and path_length == result_lenth +1 :
            option_type = get_option_type(path[-2])
        if option_type == "linechart":
            for key, df in last_key_data.items():
                key = key.split('/')
                title_pre = '_'.join(key[-3:])
                if isinstance(df, pd.DataFrame):
                    transform_data(title_pre, df, df_data)
                else:
                    df_dict = df.to_dict(orient='records')
                    df_data.append((None, key, df_dict))
            return jsonify({
                "option_type": option_type,
                "results": df_data
            })
        elif option_type == "heatmap":
            for key, df in last_key_data.items():
                key = key.split('/')
                title_pre = '_'.join(key[-3:])
                datasets = transform_data_heatmap(title_pre, df)
                print('热力图', datasets)
                df_data.append(datasets)
            return jsonify({
                "option_type": option_type,
                "results": df_data
            })
        elif option_type == "table":
            df = {'_'.join(key.split('/')[-3:]): df.to_json(orient='split') for key, df in last_key_data.items() if df is not None}
            print('table')
            return jsonify({
                "option_type": option_type,
                "results": df
            })
        elif option_type == "per_table":
            df = {}
            selected_list = []  # 初始化选定因子列表
            # 循环遍历 last_key_data 字典中的键值对
            performance_type = ""
            for key, df_data in last_key_data.items():
                if df_data is not None:
                    key_parts = key.split('/')
                    performance_type, selected_factor = key_parts[-2], key_parts[-3]
                    selected_list.append(selected_factor)  # 将 selected_factor 添加到选定因子列表中
                    new_key = '_'.join(key_parts[-3:])
                    df[new_key] = df_data.to_json(orient='split')
            if session.get('columnName'):
                # 循环结束后生成 session
                session['performance_type'] = performance_type  # 使用最后一次循环中的 performance_type
                session['selected_factor'] = selected_list  # 使用选定因子列表
                print('选定', session['performance_type'])
                print('选定1', merged_performance[session['performance_type']])
                print('选定2', merged_performance[session['performance_type']]['alltime'])
                df['total'] = filter_performance_tb(merged_performance[session['performance_type']]['alltime']).to_json(orient='split')
            print('table')
            return jsonify({
                "option_type": 'table',
                "results": df
            })
        return ''

    return app