import easyocr
import cv2
import numpy as np

vidcap = cv2.VideoCapture('/mnt/c/Users/Edgar/Downloads/videoplayback.webm')
reader = easyocr.Reader(['en'])

# result = reader.readtext('/mnt/c/Users/Edgar/Desktop/test_image3.png', detail=0)
# print(result)

# Frame in which the battles start, just to make things more efficient than scanning the whole VOD.
# This is considering the VOD is a 60 FPS video.
start = 12600
count = 0

fps_in = vidcap.get(cv2.CAP_PROP_FPS)  # Grab the video's frame rate.
fps_out = 1  # We're only interested in one frame per second of the video.

index_in = -1
index_out = -1

vidcap.set(cv2.CAP_PROP_POS_FRAMES, start)  # Moving the first frame to be captured to the beginning of the battles.
success = vidcap.grab()  # Doing a sanity check of grabbing the first frame correctly.

blue_lower = np.array([94, 80, 2], np.uint8)
blue_upper = np.array([120, 255, 255], np.uint8)

ray_event_counters = {
    'critical_hit': 0,
    'miss': 0,
    'freeze': 0,
    'paralyze': 0,
    'poison': 0,
    'burn': 0,
    'sleep': 0,
    'one_hit_ko': 0,
    'confused_self_hit': 0
}

chat_event_counters = {
    'critical_hit': 0,
    'miss': 0,
    'freeze': 0,
    'paralyze': 0,
    'poison': 0,
    'burn': 0,
    'sleep': 0,
    'one_hit_ko': 0,
    'confused_self_hit': 0
}

while success:
    success = vidcap.grab()
    index_in += 1

    out_due = int(index_in / fps_in * fps_out)
    if out_due > index_out:
        success, frame = vidcap.retrieve()
        if not success:
            break
        index_out += 1
        cropped_frame = frame[800:1000, 630:1750]  # Crop only the game screen
        result = reader.readtext(cropped_frame, detail=0)
        if 0 < len(result) < 4:
            print('Read frame ' + str(count))
            print(result)
            save_frame = False
            events = {
                'critical_hit': False,
                'miss': False,
                'freeze': False,
                'paralyze': False,
                'poison': False,
                'burn': False,
                'sleep': False,
                'one_hit_ko': False,
                'confused_self_hit': False
            }
            for detected_text in result:
                detected_event = ''
                if 'riticalhit' in detected_text:
                    print("Found a critical hit!")
                    events['critical_hit'] = True
                    detected_event = "critical_hit"
                elif 'miss' in detected_text:
                    print("Found a missed attack!")
                    events['miss'] = True
                    detected_event = "miss"
                elif 'maynot' in detected_text:
                    print("Found a paralysis effect!")
                    events['paralyze'] = True
                    detected_event = "paralyze"
                elif 'poisone' in detected_text:
                    print("Found a poison effect!")
                    events['poison'] = True
                    detected_event = "poison"
                elif 'burne' in detected_text or 'bukne' in detected_text:
                    print("Found a burn effect!")
                    events['burn'] = True
                    detected_event = "burn"
                elif 'ellaslee' in detected_text:
                    print("Found a sleep effect!")
                    events['sleep'] = True
                    detected_event = "sleep"
                elif 'KO' in detected_text:
                    print("Found a one-hit KO!")
                    events['one_hit_ko'] = True
                    detected_event = "one_hit_ko"
                elif 'Itwas' in detected_text:
                    print("Found a freeze!")
                    events['freeze'] = True
                    detected_event = "freeze"
                elif 'ackedi' in detected_text:
                    print("Found a confused self-hit!")
                    events['confused_self_hit'] = True
                    detected_event = "confused_self_hit"
                if detected_event:
                    (b, g, r) = frame[900, 1190]
                    if b > g:
                        print("Ray got a " + detected_event)
                        ray_event_counters[detected_event] += 1
                    else:
                        print("Chat got a " + detected_event)
                        chat_event_counters[detected_event] += 1
            if any(events.values()):
                milis = vidcap.get(cv2.CAP_PROP_POS_MSEC)
                events_string = ''
                for event in events:
                    if events[event]:
                        events_string += event
                cv2.imwrite("frame{0}-milis{1}-{2}.jpg".format(count, milis, events_string), cropped_frame)
            success, frame = vidcap.retrieve()
            index_out += 1
        count += 1

print("Ray events:")
print(ray_event_counters)
print("Chat events:")
print(chat_event_counters)
