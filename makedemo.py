# coding=utf-8
from __future__ import unicode_literals

import os
import glob
import pinyin
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import codecs
from collections import OrderedDict


def list_base(src_folder):
    for folder in glob.glob(src_folder):
        if os.path.isdir(folder):
            yield folder


def list_a_directory(src_folder):
    for f in glob.glob(src_folder):
        file_name = os.path.basename(f).split('.')[0]
        if '市' in file_name:
            file_name = file_name[:-1]
        pinyin_name = pinyin.get(file_name, format="numerical", delimiter="_")
        yield f, file_name, pinyin_name


def minify_js(src_js, min_js):
    os.system('./node_modules/.bin/minify -o %s %s' % (min_js, src_js))


if __name__ == '__main__':
    name_dict = {}
    raw_rendering_dict = defaultdict(list)
    for folder in list_base('src/*'):
        cfolder = os.path.basename(folder)
        pfolder = pinyin.get(cfolder, format="numerical", delimiter="_")
        _dest_folder = os.path.join('dist', pfolder)
        name_dict[cfolder] = pfolder
        if not os.path.exists(_dest_folder):
            os.mkdir(_dest_folder)
        all_files = list_a_directory(os.path.join(folder, "*.js"))
        for src_file, cname, pname in all_files:
            _dest_file = os.path.join(_dest_folder, "%s.min.js" % pname)
            print("%s-> %s, %s -> %s" % (cname, pname, src_file, _dest_file))
            minify_js(src_file, _dest_file)
            raw_rendering_dict[cfolder].append((cname, pname))
    # statistics
    count = 0
    rendering_dict = OrderedDict()
    sorted_provinces = sorted(raw_rendering_dict.keys(),
                              key=lambda x: pinyin.get(x, format='numerical'))
    for cprovince in sorted_provinces:
        count += len(raw_rendering_dict[cprovince])
        rendering_dict[cprovince] = sorted(
            raw_rendering_dict[cprovince], key=lambda x: x[1])
    provinces, cities = len(rendering_dict.keys()), count

    jinja2_env = Environment(
        loader=FileSystemLoader('./templates'),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True)
    template = jinja2_env.get_template('index.html')
    html = template.render(names=name_dict, registry=rendering_dict,
                           num_cities=cities)
    with codecs.open('index.html', 'wb', 'utf-8') as f:
        f.write(html)

    config = jinja2_env.get_template('config.json')
    config_json = config.render(names=name_dict, registry=rendering_dict)
    with codecs.open(os.path.join('dist', 'config.json'), 'wb', 'utf-8') as f:
        f.write(config_json)

    readme = jinja2_env.get_template('README.md')
    readme_txt = readme.render(
        names=name_dict, registry=rendering_dict,
        num_provinces=provinces, num_cities=cities
    )
    with codecs.open(os.path.join('README.md'), 'wb', 'utf-8') as f:
        f.write(readme_txt)
