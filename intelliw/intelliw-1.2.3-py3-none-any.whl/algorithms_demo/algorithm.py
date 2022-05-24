from intelliw import Application

logger = None
class Algorithm:
    """
    算法类， 导入的算法必须定义class Algorithm， 并放入 algorithm.py 文件中
    """

    def __init__(self, parameters):
        """
        初始化， parameters 为 dict格式的参数信息， 比如
        {
            "params1": "value1",
            "params1", 2
        }
        """
        self.parameters = parameters
        global logger
        logger = self.parameters['framework_log']   # 日志
        pass

    def load(self, path):
        """
        加载模型
            不需要调用，只需要在这里实现加载模型的方法，并赋值给一个属性就可以，例如：
            self.model = xxxx.load(path)
            上线流程：算法框架会将模型文件放在model/下，然后进行函数的执行
            本地流程：可以通过model.yaml中location字段进行配置，然后会传入path参数
            Args:
                path : 模型文件路径，根据 model.yaml 文件中的 location 字段指定
            Returns:
                无
        """
        pass

    def save(self, path):
        """
        保存模型， 保存为 path 的文件或文件夹会被框架程序自动打包上传到服务器
        如果是path是文件夹，需要加上/， 系统会创建该文件夹
            Args:
                path : 模型文件路径， 文件名或文件夹名，根据算法自定义
            Returns:
                无
        """
        pass

    def train(self, train_data, val_data, **kwargs):
        """
        模型训练
            Args:
                train_data : 训练数据
                val_data : 验证数据
                [{
                    "meta": [   // 表头
                        {"code": "column_a"},
                        {"code": "column_b"}
                    ],
                    "result": [ // 表体
                        ["line_1_column_1", "line_1_column_2"],
                        ["line_2_column_1", "line_2_column_2"]
                    ]
                },...]

                kwargs: 特征工程后返回的数据
                {
                    "final_target_col": 3,       // 目标列下标
                    "category_cols": [1,2,3]     // 类别列下标
                    "column_meta": [Employee_ID,Gender,Age,...]    // 原始数据的列名
                    "column_relation_df": Dataframe   // the map between the input columns and output columns, if column is droped, it will not exist in column_relation_df!
                }
            Returns:
                无
        """
        pass

    @Application.route("/predict", method="post", need_featrue=True)
    def infer(self, infer_data):
        """
        推理
            Args:
                infer_data : 推理请求数据, json输入的参数, 类型可以为列表/字符串/字典
                
                如果使用特征工程, infer_data格式有硬性要求:
                {
                    "data": 任意格式，如果配置特征工程，此数据为处理后的数据 # 推理数据
                    "original_data":  原始输入的data ，防止数据在通过特征处理后丢失原先的数据
                }

                self.request dict[str, object]: 请求体
                    |- self.request.header  object: 请求头
                    |- self.request.files   List[file]: form-data 文件列表
                    |- self.request.query   Dict: url参数
                    |- self.request.form    Dict: form表单参数
                    |- self.request.json    object: json参数
            Returns:
                推理结果, json
        """
        pass

    def report_train_info(self, loss, lr, iter, batchsize=1):
        """
        上报训练信息
            Args:
                loss： 损失函数loss值
                lr： 学习率
                iter： 当前iteration
                batchsize： 每批次数据量大小
            Returns:
                无
        """
        pass

    def report_val_info(self, **kwargs):
        """
        上报验证信息
            Args:
                无
            Returns:
                无
        """
        pass


