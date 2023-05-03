from io import BytesIO
#from sched_gen import generate_schedules
from PIL import Image, ImageDraw, ImageFont
from math import floor, ceil

RED = (255,153,153)
YELLOW = (255,255,153)
GREEN = (153,255,153)
BLUE = (153,204,255)
PURPLE = (204,153,255)
PINK = (255,153,204)
TURQUOISE = (153,255,204)
ORANGE = (255,204,153)
DARKBLUE = (153,153,255)
CYAN = (204,255,255)
HOUR_PADDING = 1

left_margin_offset = 148
top_margin_offset = 90
box_width = 200
vertical_length_50 = 101

color_scheme = (RED, YELLOW, GREEN, BLUE, PURPLE, PINK, TURQUOISE, ORANGE, DARKBLUE, CYAN)
day_lookup = {'U': 0, 'M':1, 'T':2, 'W':3, 'H':4, 'F':5, 'S':6}

font = ImageFont.truetype("fonts/tahoma.ttf", 19)

def str_t_to_int(str_t):
    h = int(str_t[0:2])
    m = int(str_t[3:5])
    pm = str_t[6:9] == 'PM'
    if pm and h==12: return h*60+m
    if pm and h<12: return (h+12)*60+m
    if not pm and h==12: return m
    if not pm and h<12: return h*60+m
    return None

def get_draw_text(course_class, location=''):
    course_name = course_class['course']
    class_component = course_class['component']
    class_section = course_class['section']
    class_id = course_class['class']
    instructor = course_class['instructorName']
    if instructor:
        instructor = instructor[2:-2]
    instructor_text = ''
    if instructor:
        instructor_full = instructor.split()
        instructor_initials = []
        for i in range(len(instructor_full)-1):
            instructor_initials.append(instructor_full[i][0].upper() + '. ')
        instructor_text = ''.join(instructor_initials) + instructor_full[-1]
        if font.getsize(instructor_text)[0] > box_width-3: # pop until fit with elipses
            while font.getsize(instructor_text + '...')[0] > box_width-3:
                instructor_text = instructor_text[:-1]
            instructor_text += '...'

    location = location  if location else ''
    text = course_name + '\n' + class_component + ' ' + class_section +\
        ' (' + class_id + ')\n' + location + '\n' + instructor_text
    return text.upper()

def draw_schedule(sched):
    image = Image.open("boilerplate_full.png")
    draw = ImageDraw.Draw(image)
    min_y = 2147483647
    max_y = -2147483648
    class_on_weekend = False
    course_itr = 0
    curr_course = None
    classes = sched
    for course_class in classes:
        course_class = course_class['objects']

        course_id = course_class['course']
        if course_id != curr_course:
            color = color_scheme[course_itr%len(color_scheme)]
            curr_course = course_id
            course_itr += 1
        for classtime in course_class['classtimes']:
            start_t = str_t_to_int(classtime['startTime'])
            end_t = str_t_to_int(classtime['endTime'])
            days = classtime['day']
            location = classtime['location']
            max_y = max(max_y, end_t)
            min_y = min(min_y, start_t)
            if end_t == -1: # Asynchronous classes
                continue
            for day in days:
                if day == 'S' or day == 'U':
                    class_on_weekend = True
                r_x0 = left_margin_offset + day_lookup[day] * box_width + day_lookup[day]*2
                r_x1 = r_x0 + box_width-1

                assert start_t % 15 == 0, "Start time must be a multiple of 15 minutes"
                quarters_past = start_t//15
                quarters_fill = ceil((end_t - start_t) / 15)
                r_y0 = top_margin_offset + quarters_past*25.25 + (quarters_past/4) * 3
                r_y1 = r_y0 + quarters_fill*25.25 + (quarters_fill/4 - 1) * 3

                draw.rectangle([(r_x0-2, r_y0-2), (r_x1+2, r_y1+2)], fill=(0,0,0))
                draw.rectangle([(r_x0, r_y0), (r_x1, r_y1)], fill = color)
                location = location if location else 'TBD'
                draw.text((r_x0+4, r_y0+2), get_draw_text(course_class, location=location), (0,0,0), font=font)

    # get the y region
    boilerplate_width, boilerplate_height = image.size
    top_hours = min(8, floor(min_y/60))
    y_region_top = top_margin_offset + top_hours * vertical_length_50 + top_hours*3
    bottom_hours = (ceil(max_y/60) + HOUR_PADDING)
    y_region_bottom = top_margin_offset + bottom_hours * vertical_length_50 + bottom_hours*3
    y_region = image.crop((0, y_region_top, boilerplate_width, y_region_bottom))
    y_region_length = y_region_bottom-y_region_top
    # paste the y region
    image.paste(y_region, (0, top_margin_offset, boilerplate_width, top_margin_offset+y_region_length))
    y_crop_line = top_margin_offset + y_region_length
    draw.line((0,y_crop_line-2, boilerplate_width, y_crop_line-2), fill=(0, 0, 0), width=2)
    image = image.crop((0, 0, boilerplate_width, y_crop_line))
    # crop weekend if no classes
    if not class_on_weekend:
        x_region_left = left_margin_offset + box_width + 2
        x_region_right = boilerplate_width - box_width - 2
        x_region_length = x_region_right - x_region_left
        x_region = image.crop((x_region_left, 0, x_region_right, y_crop_line))
        image.paste(x_region, (left_margin_offset, 0, left_margin_offset+x_region_length, y_crop_line))
        image = image.crop((0, 0, left_margin_offset + x_region_length, y_crop_line))
    image.save("schedule.png")
    return image

