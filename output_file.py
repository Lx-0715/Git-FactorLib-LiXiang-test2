import pickle
def output_func(result_dir, output_file_path):
    # 将结果字典保存到一个 pickle 文件中
    with open(output_file_path, 'wb') as f:
        pickle.dump(result_dir, f)
    return result_dir

