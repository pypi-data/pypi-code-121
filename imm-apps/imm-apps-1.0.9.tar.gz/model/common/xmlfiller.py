class XmlFiller():
    def __init__(self,template,context):
        self.template=template
        self.context=context
        
    def save(self,output):
        with open(self.template) as x:
            text=x.read()
            outtext=text.format(**self.context)
        with open(output,'w')as w:
            w.write(outtext)
            print(f' {output} Saved')
