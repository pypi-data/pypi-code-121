print('请确保已经安装了qrcode,pillow,MyQR模块，否则此功能将无法运行')
print('')
print('Make sure that you have installed the qrcode,pillow,MyQR module, otherwise this feature will not work')
print('')
print('==========================================================================================')
print('按enter确认已经安装，可以正常运行，否则请先安装qrcode,pillow,MyQR第三方库')
print('')
print('Press enter to confirm that it has been installed and can work normally, otherwise please install the '
      'qrcode,pillow,MyQR '
      + '\n' + 'third-party library first')
input('')
print('==========================================================================================')


def QR():
    """
    from lzlzhn import QR
    QR.QR()
    """
    import tkinter as tk
    import tkinter.filedialog as tkfiledialog
    import qrcode
    from PIL import Image
    from MyQR import myqr
    import os

    # 生成面板
    window = tk.Tk()
    # 面板名称
    window.title('二维码生成器')
    # 面板大小
    window.geometry('300x300')

    #
    text = tk.Label(window, text='输入信息', font=20)
    text.place(x=120, y=30, anchor='nw')
    inputs = tk.Entry(window, show=None, font=16)
    inputs.place(x=70, y=60, anchor='nw')

    text_root = tk.Label(window, text='输入图片路径', font=14)
    text_root.place(x=100, y=110, anchor='nw')

    e = tk.StringVar()
    text_img = tk.Entry(window, textvariable=e, font=16)
    text_img.place(x=70, y=145, anchor='nw')

    def choose_file():
        selectFileName = tkfiledialog.askopenfilename(title='选择文件')  # 选择文件
        e.set(selectFileName)

    submit_button = tk.Button(window, text="选择图片", command=choose_file)
    submit_button.place(x=120, y=170, anchor='nw')

    def getQrcode(data, file_name, imgurl):
        # 实例化QRCode生成qr对象
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        # 传入数据
        qr.add_data(data)
        # 填充数据
        qr.make(fit=True)
        # 生成二维码
        img = qr.make_image(fill_color="green", back_color="white")

        if imgurl:
            # 添加logo，打开logo照片
            icon = Image.open(imgurl)
            # 获取图片的宽高
            img_w, img_h = img.size
            # 参数设置logo的大小
            factor = 6
            size_w = int(img_w / factor)
            size_h = int(img_h / factor)
            icon_w, icon_h = icon.size
            if icon_w > size_w:
                icon_w = size_w
            if icon_h > size_h:
                icon_h = size_h
            # 重新设置logo的尺寸
            icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
            # 得到画图的x，y坐标，居中显示
            w = int((img_w - icon_w) / 2)
            h = int((img_h - icon_h) / 2)
            # 黏贴logo照
            img.paste(icon, (w, h), mask=None)

        # 保存二维码
        img.save(file_name)
        # 展示二维码
        img.show()

    def getQrcode2(data, file_name, imgurl):
        myqr.run(
            words=data,
            version=20,
            level='H',
            picture=imgurl,
            colorized=True,
            save_name=file_name,
            contrast=1.0,
            brightness=1.0,
        )

    def hit():
        # print(inputs.get())
        # print(text_img.get())
        data = inputs.get()
        imgurl = text_img.get()
        if data == '':
            data = '请输入信息'
        getQrcode(data, 'text1.png', imgurl)

    def hit2():
        data = inputs.get()
        imgurl = text_img.get()
        if data == '':
            data = '请输入信息'
        getQrcode2(data, 'text2.png', imgurl)

    but = tk.Button(window, text="生成", font=16, width=10, height=1, command=hit)
    but2 = tk.Button(window, text="生成2", font=16, width=10, height=1, command=hit2)

    but.place(x=105, y=220, anchor='nw')
    but2.place(x=105, y=260, anchor='nw')

    window.mainloop()
