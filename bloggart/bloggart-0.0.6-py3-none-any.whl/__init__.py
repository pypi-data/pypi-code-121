"""bloggart command line interface."""
from bloggart import kernel

# def main():
#     app=make_app()  #建立Application对象
#     app.listen(8888) #设置监听端口
#     try:
#         #启动IOLoop
#         tornado.ioloop.IOLoop.current().start()
#     except KeyboardInterrupt:
#         tornado.ioloop.IOLoop.current().stop()
#         #此处执行资源回收工作
#         print("Program exit!")

def main():
    """Entry point for the application script"""
    print("Call your main application code here")
    kernel.Run()
    exit()

    # args = parser.parse_args()

    # if args.quiet:
    #     jieba.setLogLevel(60)
    # if args.pos:
    #     import jieba.posseg
    #     posdelim = args.pos
    #     def cutfunc(sentence, _, HMM=True):
    #         for w, f in jieba.posseg.cut(sentence, HMM):
    #             yield w + posdelim + f
    # else:
    #     cutfunc = jieba.cut

    # delim = text_type(args.delimiter)
    # cutall = args.cutall
    # hmm = args.hmm
    # fp = open(args.filename, 'r') if args.filename else sys.stdin

    # if args.dict:
    #     jieba.initialize(args.dict)
    # else:
    #     jieba.initialize()
    # if args.user_dict:
    #     jieba.load_userdict(args.user_dict)

    # ln = fp.readline()
    # while ln:
    #     l = ln.rstrip('\r\n')
    #     result = delim.join(cutfunc(ln.rstrip('\r\n'), cutall, hmm))
    #     if PY2:
    #         result = result.encode(default_encoding)
    #     print(result)
    #     ln = fp.readline()

    # fp.close()

