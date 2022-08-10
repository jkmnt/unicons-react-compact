import json
import os
import xml.etree.ElementTree as ET
import argparse

TEMPLATE = r'''
// autgenerated from https://github.com/Iconscout/unicons

import React from 'react';

const UniconsArt = %s;

export type UniconsNames = keyof typeof UniconsArt;

export const Unicons = (props: React.HTMLAttributes<SVGElement> & { name: UniconsNames; size?: number | string }) => {
  const { color = 'currentColor', size = 24, name, ...rest } = props;

  return React.createElement(
    'svg',
    {
      width: size,
      height: size,
      viewBox: '0 0 24 24',
      fill: color,
      ...rest,
    },
    React.createElement('path', { d: UniconsArt[name] })
  );
};
'''

def extract_art(spec, srcdir):
    name = spec['name']
    svgpath = os.path.join(srcdir, spec['svg'])
    tree = ET.parse(svgpath)
    root = tree.getroot()
    path_ = tree.find('{http://www.w3.org/2000/svg}path')
    if path_ is None:
        print('failed to parse %s' % svgpath)
        return None
    d = path_.attrib['d']
    return d

def main():
    parser = argparse.ArgumentParser(description='generate react-unicons-compact')
    parser.add_argument('src', help='path to local clone of unicons svg repository', type=str)
    parser.add_argument('dst', help='resulting ts file', type=str)
    parser.add_argument('--exclude', help='exclude icon from build (repeat for more icons)', type=str, action='append')
    args = parser.parse_args()

    exclude = args.exclude or []

    with open(os.path.join(args.src, 'json/line.json'), encoding='utf8') as f:
        spec = json.load(f)

    result = {}

    for s in spec:
        name = s['name']
        if name in exclude:
            continue
        d = extract_art(s, args.src)
        if d:
            result[name] = d

    content = TEMPLATE % json.dumps(result, separators=(',', ':'))

    with open(args.dst, 'w', encoding='utf8') as f:
        f.write(content)


main()