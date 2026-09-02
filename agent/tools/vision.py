from langchain_core.tools import tool

@tool
def parse_order_image(image_path):
    """
    识别单据图像的具体内容信息
    输入：
        image_path. 表示图片的路径
    输出：
        单据信息，以json格式输出
    """
    print('调用InternVL3模型进行图像识别')
    csv = '公司1, 公司2, 钢笔, 4, 500'    # 模拟单据中只有一个货物 # 这里调用使用internvl3的api函数
    order_json = {
        '商品名称': '钢笔',
        '单价': 4
    }
    return order_json