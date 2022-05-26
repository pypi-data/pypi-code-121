from ModisDownload.InitCHN import Init
from ModisDownload.PolygonUtiles import Poly
from ModisDownload.SearchCHN import SearchData,SearchChina,Login
from ModisDownload.Base import Sensors
from ModisDownload import visited

def downloadModisExample(token:str):
    # 初始化组件 如果查询不到相应的产品请使用此API更新相关信息
    # visited.reload()
    # 查询可下载产品名称
    # a=visited.search_p()
    # 查询可下载区域
    # b=visited.search_area()
    # 初始化下载对象
    g = visited.getHtml(token)
    # 下载主方法 一定需要写在 if __name__ == '__main__': 下 否则多进程报错
    g.download_main("MOD16A2", "2008-01-01..2008-01-31", "china", "package/", thread_num=4, max_try=100)
    return

def searchChinaExample():
    # 更新传感器相关信息
    Init(False)

    # 登录
    login = loginTest("irsaadmin", "qrst@2014")

    # 绘制ROI区域包括点,矩形,多边形
    # 点a
    geom = Poly.Point(114.220090, 30.305615)
    # 多边形
    geom2 = Poly.Polygon(
        [[105.550278, 32.174096], [105.550278, 28.707072], [109.525337, 28.707072], [109.525337, 32.174096]])
    # 矩形 左上角经度，左上角纬度，右下角经度，右下角纬度
    geom3 = Poly.Square(104.550278, 28.174096, 109.525337, 18.707072)

    # 查询元数据
    # 开始日期，结束日期，[查询载荷列表 可以手动输入字符]，ROI区域，云量，产品等级
    searchData = SearchData("2020-05-11", "2022-05-21",
                            [Sensors.HJ2A_HSI,Sensors.HJ2A_CCD]
                            , [geom,geom2,geom3], 100, 1,login=login)

    # 初始化查询
    search = SearchChina(searchData, False)
    # 查询
    search.search()
    # 保存结果
    search.save_ans("ans.csv")
    # 答应
    print("查询完成")
    return

def loginTest(username,password):
    login=Login(username,password)
    return login


if __name__ == '__main__':
    searchChinaExample()
    # downloadModisExample("")
    # login=loginTest("irsaadmin","qrst@2014")

