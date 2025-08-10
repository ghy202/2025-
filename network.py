import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import joblib
import json

# 使用新数据（data1.xlsx）并移除"喜欢"手势
data = {
    "手势": [
        "OK", "", "", "", "",
        "你", "", "", "", "",
        "谢谢", "", "", "", "",
        "明天见", "", "", "", "",
        "好", "", "", "", "",
        "对不起", "", "", "", "",
        "没关系", "", "", "", ""
    ],
    "编号": [
        1, 1, 1, 1, 1,
        2, 2, 2, 2, 2,
        3, 3, 3, 3, 3,
        4, 4, 4, 4, 4,
        5, 5, 5, 5, 5,
        6, 6, 6, 6, 6,
        7, 7, 7, 7, 7
    ],
    "A1": [
        331, 332, 352, 355, 351,
        636, 346, 652, 647, 670,
        635, 632, 628, 625, 635,
        314, 311, 310, 311, 312,
        502, 501, 500, 499, 496,
        312, 311, 310, 312, 312,
        324, 326, 327, 326, 338
    ],
    "A2": [
        303, 310, 328, 333, 326,
        865, 855, 893, 889, 902,
        835, 834, 830, 831, 835,
        272, 271, 269, 268, 269,
        822, 819, 820, 817, 820,
        793, 781, 791, 785, 783,
        339, 339, 338, 342, 338
    ],
    "A3": [
        479, 480, 444, 447, 438,
        336, 330, 336, 338, 338,
        593, 593, 592, 593, 591,
        324, 327, 326, 324, 325,
        585, 582, 584, 584, 583,
        566, 567, 565, 564, 562,
        418, 423, 417, 414, 415
    ],
    "A4": [
        959, 960, 979, 979, 978,
        973, 927, 976, 974, 975,
        975, 975, 975, 976, 975,
        346, 346, 345, 345, 346,
        346, 345, 346, 347, 345,
        969, 970, 971, 971, 972,
        975, 975, 975, 977, 977
    ]
}

def get_features_and_labels():
    """提取特征和标签，只使用A1-A4特征"""
    # 特征矩阵：只包含A1-A4四列
    features = np.array([data['A1'], data['A2'], data['A3'], data['A4']]).T
    
    # 标签向量
    labels = np.array(data['编号'])
    
    # 创建手势名称映射（移除了"喜欢"）
    sign_names = {}
    for i, gesture in enumerate(data['手势']):
        if gesture.strip():
            sign_names[data['编号'][i]] = gesture
    
    return features, labels, sign_names

def train_model():
    """训练神经网络模型"""
    X, y, sign_names = get_features_and_labels()
    
    # 创建预处理和模型管道
    model = make_pipeline(
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=42
        )
    )
    
    # 训练模型
    model.fit(X, y)
    return model, sign_names

def save_model(model, model_path='model.joblib'):
    joblib.dump(model, model_path)

def load_model(model_path='model.joblib'):
    return joblib.load(model_path)

def save_sign_mapping(sign_names, mapping_path='sign_mapping.json'):
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(sign_names, f, ensure_ascii=False)

def load_sign_mapping(mapping_path='sign_mapping.json'):
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def predict_gesture(model, sample):
    sample = np.array(sample).reshape(1, -1)
    return model.predict(sample)[0]

if __name__ == "__main__":
    # 训练并保存模型
    model, sign_names = train_model()
    save_model(model)
    save_sign_mapping(sign_names)
    
    # 测试模型
    test_sample = [331, 303, 479, 959]  # OK手势的A1-A4
    prediction = predict_gesture(model, test_sample)
    print(f"预测结果: {prediction} -> {sign_names[prediction]}")