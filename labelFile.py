# -*- coding:utf-8 -*-
import base64
import json
import os.path
import sys


PY2 = sys.version_info[0] == 2


class LabelFileError(Exception):
    pass


class LabelFile(object):

    suffix = '.json'

    def __init__(self, filename=None):
        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        if filename is not None:
            self.load(filename)
        self.filename = filename

    def load(self, filename):
        keys = [
            'imageData',
            'imagePath',
            'lineColor',
            'fillColor',
            'shapes',  # polygonal annotations
            'flags',   # image level flags
        ]
        labelUserName = ''
        qualityUserName = ''
        secondQualityUserName = ''
        companyName = ''
        title = ''
        try:
            with open(filename, 'rb' if PY2 else 'r') as f:
                data = json.load(f)
            # if data['imageData'] is not None:
            #     imageData = base64.b64decode(data['imageData'])
            # else:
            # relative path from label file to relative path from cwd
            imagePath = os.path.join(os.path.dirname(filename),
                                     data['imagePath'])
            with open(imagePath, 'rb') as f:
                imageData = f.read()
            flags = data.get('flags')
            imagePath = data['imagePath']
            lineColor = data['lineColor']
            fillColor = data['fillColor']
            if 'labelUserName' in data:
                labelUserName = data['labelUserName']
            if 'qualityUserName' in data:
                qualityUserName = data['qualityUserName']
            if 'secondQualityUserName' in data:
                secondQualityUserName = data['secondQualityUserName']
            if 'companyName' in data:
                companyName = data['companyName']
            if 'title' in data:
                title = data['title']
            shapes = (
                (s['label'], s['points'], s['line_color'], s['fill_color'])
                for s in data['shapes']
            )
        except Exception as e:
            raise LabelFileError(e)

        otherData = {}
        for key, value in data.items():
            if key not in keys:
                otherData[key] = value

        # Only replace data after everything is loaded.
        self.flags = flags
        self.shapes = shapes
        self.imagePath = imagePath
        self.imageData = imageData
        self.lineColor = lineColor
        self.fillColor = fillColor
        self.filename = filename
        self.otherData = otherData
        self.labelUserName = labelUserName if labelUserName is not None else ''
        self.qualityUserName = qualityUserName if qualityUserName is not None else ''
        self.secondQualityUserName = secondQualityUserName if secondQualityUserName is not None else ''
        self.companyName = companyName if companyName is not None else ''
        self.title = title if title is not None else ''

    def save(self, imgWidth, imgHeight, filename, shapes, imagePath, imageData=None,
             lineColor=None, fillColor=None, otherData=None,
             flags=None):
        # if imageData is not None:
        #     imageData = base64.b64encode(imageData).decode('utf-8')
        if otherData is None:
            otherData = {}
        if flags is None:
            flags = []
        data = dict(
            flags=flags,
            shapes=shapes,
            lineColor=lineColor,
            fillColor=fillColor,
            imagePath=imagePath,
            # imageData=imageData,
            imgWidth=imgWidth,
            imgHeight=imgHeight
        )
        # labelUserName = self.labelUserName,
        # qualityUserName = self.qualityUserName,
        # secondQualityUserName = self.secondQualityUserName,
        # companyName = self.companyName,
        # title = self.title,
        for key, value in otherData.items():
            data[key] = value
        try:
            with open(filename, 'wb' if PY2 else 'w') as f:
                # json.dump(data, f, ensure_ascii=False, indent=2)
                json.dump(data, f, indent=4)
            self.filename = filename
        except Exception as e:
            raise LabelFileError(e)

    @staticmethod
    def isLabelFile(filename):
        return os.path.splitext(filename)[1].lower() == LabelFile.suffix
