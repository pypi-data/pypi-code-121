from math import sin, cos, radians


class Svg:
    count = 0

    def __init__(self, name, w, h):
        self.name = name
        self.width = w
        self.height = h
        self.styles = []
        self.defs = []
        self.objects = []
        Svg.count += 1

    def addStyle(self, className, css):
        self.styles.append(f'.{className} {{{css}}}')

    def addDefs(self, text):
        self.defs.append(text)

    def addObjectText(self, objText):
        self.objects.append(objText)

    def openGroup(self, **attrs):
        self.addObjectText(f'<g  {Svg.manageAttrs(attrs)}>')

    def closeGroup(self):
        self.addObjectText('</g>')

    def rgb2hex(rgb):
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        hex_ = f'#{r:02x}{g:02x}{b:02x}'
        return hex_

    def text(self, **attrs):
        saveattrs = {
            "viewBox": f"0 0 {self.width} {self.height}"
        }

        for key in attrs:
            saveattrs[key] = attrs[key]

        allStyles = "\n".join(self.styles)
        allDefs = "\n".join(self.defs)

        self.svg = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<svg {Svg.manageAttrs(saveattrs)} xml:space="preserve" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">',
            '<defs>',
            '' if len(
                self.styles) == 0 else f'<style type="text/css" >\n{allStyles}\n</style>',
            '' if len(self.styles) == 0 else allDefs,
            '</defs>',
            '\n'.join(self.objects),
            '</svg>',
        ]
        return '\n'.join(self.svg)

    def save(self, direction='', **attrs):
        name = f'{direction}/{self.name}.svg' if direction != '' else f'{self.name}.svg'
        with open(name, "w", encoding="utf-8") as svgFile:
            svgFile.write(self.text(**attrs))

    def clearAttrs(attrs):
        for _ in range(20):
            if '_attrs' in attrs.keys():
                attrs = attrs['_attrs']
            else:
                break
        return attrs

    def manageAttrs(attrs):
        attrs = Svg.clearAttrs(attrs)

        _attrs = ''
        for key in attrs.keys():
            if key == 'class_':
                _attrs += f'class="{attrs[key]}" '
            else:
                _attrs += f'{key}="{attrs[key]}" '
        return _attrs

    def removeDuplicate(points):
        newPoints = [points[0]]
        for i in range(1, len(points)):
            if newPoints[-1] != points[i]:
                newPoints.append(points[i])

        return newPoints

    def managePoints(points):
        _points = ''
        for point in points:
            _points += f'{point[0]},{point[1]} '
        return _points

    def addComment(self, comment):
        self.addObjectText(f'<!-- {comment} -->')

    def addText(self, x, y, Text, **attrs):
        textStr = f'<text x="{x}" y="{y}" {Svg.manageAttrs(attrs)}>{Text}</text>'
        self.addObjectText(textStr)

    def addCircle(self, cx, cy, r, **attrs):
        circleStr = f'<circle cx="{cx}" cy="{cy}" r="{r}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(circleStr)

    def addRect(self, x, y, w, h, **attrs):
        rectStr = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(rectStr)

    def addEllipse(self, cx, cy, rx, ry, **attrs):
        ellipseStr = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(ellipseStr)

    def addLine(self, x1, y1, x2, y2, **attrs):
        lineStr = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(lineStr)

    def addPolygon(self, points, **attrs):
        points = Svg.removeDuplicate(points)
        polygonStr = f'<polygon points="{Svg.managePoints(points)}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(polygonStr)

    def addPolyline(self, points, **attrs):
        points = Svg.removeDuplicate(points)
        polylineStr = f'<polyline points="{Svg.managePoints(points)}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(polylineStr)

    def addPathByD(self, d, **attrs):
        arcStr = f'<path d="{d}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(arcStr)

    def addNormalArc(self, cx, cy, rx, ry, startDegree, endDegree, **attrs):
        _start = (cx + rx * cos(radians(startDegree)),
                  cy - ry * sin(radians(startDegree)))
        _end = (cx + rx * cos(radians(endDegree)),
                cy - ry * sin(radians(endDegree)))
        sweepFlag = 0 if endDegree > startDegree else 1
        largeArcFlag = 0 if endDegree - startDegree < 180 else 1
        arcStr = f'<path d="M {_start[0]},{_start[1]} A {rx},{ry} 0 {largeArcFlag} {sweepFlag} {_end[0]},{_end[1]}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(arcStr)

    def addArc(self, x1, y1, rx, ry, xAxisRotation, largeArcFlag, sweepFlag, x2, y2, **attrs):
        arcStr = f'<path d="M {x1},{y1} A {rx},{ry} {xAxisRotation} {largeArcFlag} {sweepFlag} {x2},{y2}" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(arcStr)

    def addBezier(self, points, *data, **attrs):
        if len(data) == 0:
            data = ('', '')
        elif len(data) == 1:
            data = (data[0], '')

        bezierStr = '<path d="'
        if data[0] == 'q':
            if data[1] == 'smooth':  # quadric smooth
                for i in range(len(points)):
                    if i == 0:
                        bezierStr += f'M {points[i][0]},{points[i][1]}'
                    elif i == 1:
                        bezierStr += f' Q {points[i][0]},{points[i][1]}'
                    elif i == 2:
                        bezierStr += f' {points[i][0]},{points[i][1]}'
                    else:
                        bezierStr += f' T {points[i][0]},{points[i][1]}'

            else:  # quadric normal
                for i in range(len(points)):
                    if i == 0:
                        bezierStr += f'M {points[i][0]},{points[i][1]}'
                    elif i % 2 == 1:
                        bezierStr += f' Q {points[i][0]},{points[i][1]}'
                    else:
                        bezierStr += f' {points[i][0]},{points[i][1]}'

        else:
            if data[1] == 'smooth':  # cubic smooth
                for i in range(len(points)):
                    if i == 0:
                        bezierStr += f'M {points[i][0]},{points[i][1]}'
                    elif i == 1:
                        bezierStr += f' C {points[i][0]},{points[i][1]}'
                    elif i == 2:
                        bezierStr += f' {points[i][0]},{points[i][1]}'
                    elif i == 3:
                        bezierStr += f' {points[i][0]},{points[i][1]}'
                    elif i % 2 == 0:
                        bezierStr += f' S {points[i][0]},{points[i][1]}'
                    else:
                        bezierStr += f' {points[i][0]},{points[i][1]}'

            else:  # cubic normal
                for i in range(len(points)):
                    if i == 0:
                        bezierStr += f'M {points[i][0]},{points[i][1]}'
                    elif i % 3 == 1:
                        bezierStr += f' C {points[i][0]},{points[i][1]}'
                    elif i % 3 == 2:
                        bezierStr += f' {points[i][0]},{points[i][1]}'
                    else:
                        bezierStr += f' {points[i][0]},{points[i][1]}'

        bezierStr += f'" {Svg.manageAttrs(attrs)}/>'
        self.addObjectText(bezierStr)

    def addCurve(self, points, **attrs):
        try:
            import numpy as np
        except:
            print('Numpy is not installed')
            return None

        if (len(points) < 2):
            return

        scl = 0.25
        if 'scl' in attrs.keys():
            scl = attrs['scl']
        controlPoints = []

        for i in range(len(points)):
            if (i == 0):  # first
                p1 = np.array(points[i])
                p2 = np.array(points[i+1])

                tangent = p2 - p1
                q1 = p1 + scl * tangent

                controlPoints.append(p1)
                controlPoints.append(q1)

            elif (i == len(points) - 1):  # last
                p0 = np.array(points[i-1])
                p1 = np.array(points[i])

                tangent = (p1 - p0)
                q0 = p1 - scl * tangent

                controlPoints.append(q0)
                controlPoints.append(p1)

            else:
                p0 = np.array(points[i - 1])
                p1 = np.array(points[i])
                p2 = np.array(points[i + 1])

                tangent = (p2 - p0)/np.linalg.norm(p2 - p0)
                q0 = p1 - scl * tangent * np.linalg.norm(p1 - p0)
                q1 = p1 + scl * tangent * np.linalg.norm(p2 - p1)

                controlPoints.append(q0)
                controlPoints.append(p1)
                controlPoints.append(q1)

        controlPoints = controlPoints[3:-3]
        self.addBezier(controlPoints, _attrs=attrs)

    def addCloseCurve(self, points, **attrs):
        if points[0] == points[-1]:
            points = [points[-2]] + points + [points[1]]
        else:
            points = points[-2:] + points + points[:2]

        self.addCurve(points, _attrs=attrs)

    def progressbar(name, Min, no, Max, m=50):
        Min = int(Min)
        Max = int(Max)
        diff = Max-Min
        scl = m/diff

        if no >= Min and no < Max:
            bar = f'> {name:>20}:{round((100/m)*scl*(no-Min)):3}%   '
            for _ in range(round(scl*(no-Min))):
                bar += '█'
            for _ in range(round(scl*(Max-no))):
                bar += '░'
            bar += f'    {no:6}   {(no%10+1)*"#":11}          '
            print(bar, end="\r")
        else:
            print(f'> {name} Done!{(m+50)*" "}')
