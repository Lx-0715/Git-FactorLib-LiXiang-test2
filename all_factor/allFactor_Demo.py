import os
import importlib
import inspect
import sys
import config_super
import main

def all_factor_pipeline(CONFIG):
    # 获取当前工作目录的父目录
    parent_dir = os.path.dirname(os.getcwd())
    # 创建一个字典来保存所有的结果
    cal_metric_results = {}
    merged_result = {}
    # 遍历父目录及其所有子目录
    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            # 检查文件是否以 'pipeline.py' 结尾
            if file.endswith('pipeline.py') and not file.endswith('all_pipeline.py'):
                # 获取文件的完整路径
                file_path = os.path.join(root, file)

                # 解析文件的路径层级
                path_components = file_path.split(os.sep)
                path_key = path_components[path_components.index(parent_dir.split(os.sep)[-1]):][1:-1]

                # 导入 'pipeline.py' 文件
                spec = importlib.util.spec_from_file_location('pipeline', file_path)
                pipeline = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(pipeline)

                # 切换到 'pipeline.py' 文件所在的目录
                os.chdir(root)

                # 导入 'config.py' 文件
                spec = importlib.util.spec_from_file_location('config', os.path.join(root, 'config.py'))
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)

                # 合并 'config' 和 'config_super'
                config.CONFIG.update(CONFIG)

                # 获取 'pipeline.py' 文件中最外层的函数
                outer_function = None
                for name, obj in inspect.getmembers(pipeline):
                    if inspect.isfunction(obj):
                        outer_function = obj
                        break

                # 调用 'pipeline.py' 文件中的函数
                if outer_function is not None:
                    result = outer_function(config.config_custom, config.CONFIG)
                    for key, value in result.items():
                        # 将键值对添加到新字典中
                        merged_result[key] = value
                    print(merged_result)
                    # 将结果保存在字典中
                    current_level = cal_metric_results
                    for component in path_key[:]:
                        if component not in current_level:
                            current_level[component] = {}
                        current_level = current_level[component]
                    current_level[path_key[-1]] = result
                # 切换回父目录
                os.chdir(parent_dir)
    # 生成汇总表
    import merge_perfomance
    cal_metric_results['performance_total'] = merge_perfomance.merged_performance(merged_result)
    print(cal_metric_results)

    # ------------输出-------------
    # 获取当前脚本所在的目录路径
    script_directory = os.path.dirname(__file__)
    # 将当前工作目录更改为当前脚本所在的目录
    os.chdir(script_directory)
    sys.path.append(CONFIG["output_model_dir"])
    import output_file
    output_file_path = os.path.join(CONFIG['output_dir'], "cal_metric_indicator.pkl")
    cal_metric_results = output_file.output_func(cal_metric_results, output_file_path)

    return cal_metric_results

try:
    if __name__ == '__main__':
        cal_metric_results = all_factor_pipeline(config_super.CONFIG)
        # web分析
        app = main.create_app(cal_metric_results, CONFIG=config_super.CONFIG)
        app.run(debug=True)

except Exception as ex:
    import traceback
    import send_email
    # 发生异常时，发送邮件
    send_email.send_an_error_message(program_name='程序测试', error_name=repr(ex), error_detail=traceback.format_exc())
