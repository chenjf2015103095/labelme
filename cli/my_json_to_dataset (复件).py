import argparse
import base64
import json
import os
import os.path as osp
import warnings
import shutil
import PIL.Image
import yaml
import numpy as np
from labelme import utils
#import utils as util
from deeplab.utils import save_annotation
from deeplab.utils import get_dataset_colormap


# LABEL_NAMES = {
#     '_background_': 0,
#     'dadeng': 1,
#     'gangquan': 2,
#     'dangfengboli': 3,
#     'xinglixianggai': 4,
#     'jigai': 5,
#     'baoxiangang': 6,
#     'houshijing': 7,
#     'zhongwang': 8
# }
# LABEL_NAMES = np.asarray([
#     '_background_',
#     'dadeng',
#     'gangquan',
#     'dangfengboli',
#     'xinglixianggai',
#     'jigai',
#     'baoxiangang',
#     'houshijing',
#     'zhongwang'
# ])

def generate(base_dir, json_dir, output_dir):
    json_list = os.listdir(json_dir)
    total_num = 0
    label_map = {}
    abort_num = 0
    for i in range(0,len(json_list)):
        if not json_list[i].endswith('.json'):
            continue
        fname,ext = os.path.basename(json_list[i]).split('.json')
        out_dir = output_dir+'/'+fname
        if osp.exists(out_dir):
            print('exists')
            continue
        if not osp.exists(out_dir):
            os.makedirs(out_dir)
        json_file = os.path.join(json_dir,json_list[i])
        data = json.load(open(json_file))
        if data['imageData']:
            imageData = data['imageData']
        else:
            imagePath = os.path.join(os.path.dirname(json_file), data['imagePath'])
            with open(imagePath, 'rb') as f:
                imageData = f.read()
                imageData = base64.b64encode(imageData).decode('utf-8')
        img = util.img_b64_to_arr(imageData)
        label_name_to_value = {'_background_': 0}
        for shape in data['shapes']:
            label_name = shape['label']
            if label_name in label_name_to_value:
                label_value = label_name_to_value[label_name]
            else:
                label_value = len(label_name_to_value)
                label_name_to_value[label_name] = label_value
        # label_values must be dense
        label_values, label_names = [], []
        for ln, lv in sorted(label_name_to_value.items(), key=lambda x: x[1]):
            label_values.append(lv)
            label_names.append(ln)
        # assert label_values == list(range(len(label_values)))
        print(label_values)
        try:
            lbl = util.shapes_to_label(img.shape, data['shapes'], label_name_to_value)
        except Exception as ex:
            print(ex)
            abort_num += 1
            if osp.exists(out_dir):
                shutil.rmtree(out_dir)
            continue
        # label = get_dataset_colormap.create_pascal_label_colormap()
        captions = ['{}: {}'.format(lv, ln)
                    for ln, lv in label_name_to_value.items()]
        lbl_viz = util.draw_label(lbl, img, captions)

        # PIL.Image.fromarray(img).save(osp.join(out_dir, 'img.png'))
        PIL.Image.fromarray(img).save(osp.join(out_dir, 'img.jpg'))
        PIL.Image.fromarray(lbl).save(osp.join(out_dir, 'label.png'))
        PIL.Image.fromarray(lbl_viz).save(osp.join(out_dir, 'label_viz.png'))
        with open(osp.join(out_dir, 'label_names.txt'), 'w') as f:
            for lbl_name in label_names:
                f.write(lbl_name + '\n')
        warnings.warn('info.yaml is being replaced by label_names.txt')
        info = dict(label_names=label_names)
        with open(osp.join(out_dir, 'info.yaml'), 'w') as f:
            yaml.safe_dump(info, f, default_flow_style=False)
        total_num += 1
    print('total=' + str(total_num) + ',abort=' + str(abort_num))
    # for root,dirs,files in os.walk(output_dir):
    #     for f in files:
    #         if f == 'label_names.txt':
    #             with open(os.path.join(root, 'label_names.txt'),'r') as f:
    #                 for line in f:
    #                     if not label_map.has_key(line):
    #                         label_map[line] = line
    # with open(osp.join(base_dir, 'label_names.txt'), 'w') as f:
    #     f.write('_background_'+'\n')
    #     for v in label_map.values():
    #         if not v.startswith('_background_'):
    #             f.write(v)


if __name__ == '__main__':
    json_dir='/home/ubutnu/person'
    base_dir='/home/ubutnu/dataset-sample'
    out_dir=base_dir +'/data'
    generate(base_dir,json_dir, output_dir)
