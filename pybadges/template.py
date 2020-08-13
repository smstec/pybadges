# Copyright 2017-2020, Sophos Limited. All rights reserved.
#
# 'Sophos' and 'Sophos Anti-Virus' are registered trademarks of
# Sophos Limited and Sophos Group. All other product and company
# names mentioned are trademarks or registered trademarks of their
# respective owners.

""" TODO: Rewrite module docstring. """

import os
import tempfile


_BASE_TEMPLATE = [
    '{% set logo_width = XLHEIGHT if logo else 0 %}',
    '{% set logo_padding = 3 if (logo and left_text) else 0 %}',
    '{% set left_width = left_text_width + 10 + logo_width + logo_padding %}',
    '{% set right_width = right_text_width + 10 %}',
    'SET_LEFT_WIDTHS',
    'SET_RIGHT_WIDTHS',
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{{ left_width + right_width }}" height="XHEIGHT">',
    '  {% if whole_title %}',
    '    <title>{{ whole_title }}</title>',
    '  {% endif %}',
    '  <linearGradient id="smooth" x2="0" y2="100%">',
    '      <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>',
    '    <stop offset="1" stop-opacity=".1"/>',
    '  </linearGradient>',
    '',
    '  <clipPath id="round">',
    '    <rect width="{{ left_width + right_width }}" height="XHEIGHT" rx="3" fill="#fff"/>',
    '  </clipPath>',
    '',
    '  <g clip-path="url(#round)">',
    '    <rect width="{{ left_width }}" height="XHEIGHT" fill="{{ left_color }}">',
    '      {% if left_title %}',
    '        <title>{{ left_title }}</title>',
    '      {% endif %}',
    '    </rect>',
    '    <rect x="{{ left_width }}" width="{{ right_width }}" height="XHEIGHT" fill="{{ right_color }}">',
    '      {% if right_title %}',
    '        <title>{{ right_title }}</title>',
    '      {% endif %}',
    '    </rect>',
    '    <rect width="{{ left_width + right_width }}" height="XHEIGHT" fill="url(#smooth)"/>',
    '  </g>',
    '',
    '  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">',
    '    {% if logo %}',
    '      <image x="5" y="3" width="{{ logo_width}}" height="XLHEIGHT" xlink:href="{{ logo}}"/>',
    '    {% endif %}',
    'LEFT_TEXT',
    'RIGHT_TEXT',
    '',
    '  {% if left_link or whole_link %}',
    '    <a xlink:href="{{ left_link or wholelink }}">',
    '      <rect width="{{ left_width }}" height="XHEIGHT" fill="rgba(0,0,0,0)"/>',
    '    </a>',
    '  {% endif %}',
    '  {% if right_link or whole_link %}',
    '    <a xlink:href="{{ right_link or whole_link }}">',
    '      <rect x="{{ left_width }}" width="{{ right_width }}" height="XHEIGHT" fill="rgba(0,0,0,0)"/>',
    '    </a>',
    '  {% endif %}',
    '  </g>',
    '</svg>']


def write_template(left_line_count=1, right_line_count=1):
    left_line_count = max(1, left_line_count)
    rightt_line_count = max(1, right_line_count)

    line_count = max(left_line_count, right_line_count)

    _default_y = 150

    def _base(big, small):
        return _default_y + ((_default_y * (big - 1)) / (small + 1))

    if left_line_count == right_line_count:
        base_left_y = _default_y
        base_right_y = _default_y
    elif left_line_count > right_line_count:
        base_left_y = _default_y
        base_right_y = _base(left_line_count, right_line_count)
    else:
        base_left_y = _base(right_line_count, left_line_count)
        base_right_y = _default_y

    height = 10 + line_count * 15
    fd, fname = tempfile.mkstemp(suffix='.svg', text=True)

    with open(fname, 'wt') as tfile:
        for line in _BASE_TEMPLATE:
            if line == 'SET_LEFT_WIDTHS':
                for i in range(left_line_count):
                    line = ''.join(('{% set ',
                                    f'left_text_{i}_width = left_text_{i}_width ',
                                    '+ 10 + logo_width + logo_padding %}\n'))
                    tfile.write(line)
            elif line == 'SET_RIGHT_WIDTHS':
                for i in range(right_line_count):
                    line = ''.join(('{% set ',
                                    f'right_text_{i}_width = right_text_{i}_width ',
                                    '+ 10 %}\n'))
                    tfile.write(line)
            elif line == 'LEFT_TEXT':
                for i in range(left_line_count):
                    line = ''.join(('    <text x="{{ (((left_width+logo_width+logo_padding)/2)+1)*10 }}" ',
                                    f'y="{(i * 150) + base_left_y}" ',
                                    'fill="#010101" fill-opacity=".3" transform="scale(0.1)" ',
                                    'textLength="{{ (',
                                    f'left_text_{i}_width-(10+logo_width+logo_padding))*10 ',
                                    '}}" lengthAdjust="spacing">{{ ',
                                    f'left_text_{i} ',
                                    '}}</text>\n'))
                    tfile.write(line)
                    line = ''.join(('    <text x="{{ (((left_width+logo_width+logo_padding)/2)+1)*10 }}" ',
                                    f'y="{(i * 150) + base_left_y - 10}" ',
                                    'transform="scale(0.1)" textLength="{{ ',
                                    f'(left_text_{i}_width-(10+logo_width+logo_padding))*10 ',
                                    '}}" lengthAdjust="spacing">{{ ',
                                    f'left_text_{i} ',
                                    '}}</text>\n'))
                    tfile.write(line)
            elif line == 'RIGHT_TEXT':
                for i in range(right_line_count):
                    line = ''.join(('    <text x="{{ (left_width+right_width/2-1)*10 }}" ',
                                    f'y="{(i * 150) + base_right_y}" ',
                                    'fill="#010101" fill-opacity=".3" transform="scale(0.1)" ',
                                    'textLength="{{ (',
                                    f'right_text_{i}_width-10)*10 ',
                                    '}}" lengthAdjust="spacing">{{ ',
                                    f'right_text_{i} ',
                                    '}}</text>\n'))
                    tfile.write(line)
                    line = ''.join(('    <text x="{{ (left_width+right_width/2-1)*10 }}" ',
                                    f'y="{(i * 150) + base_right_y - 10}" ',
                                    'transform="scale(0.1)" textLength="{{ ',
                                    f'(right_text_{i}_width-10)*10 ',
                                    '}}" lengthAdjust="spacing">{{ ',
                                    f'right_text_{i}',
                                    '}}</text>\n'))
                    tfile.write(line)
            else:
                line = line.replace('XHEIGHT', str(height))
                line = line.replace('XLHEIGHT', str(height - 6))
                tfile.write(f'{line}\n')

    os.close(fd)
    return fname  #.split('/')[-1]


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    write_template()
