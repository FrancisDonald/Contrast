from skimage import color, exposure
import math

def brightAdapt(data, brightness):
    adaptation = int(math.sqrt(128) - math.sqrt(brightness))/3
    hdr_im = data +(adaptation, 0, 0)
    frame = color.lab2rgb(hdr_im)
    cutoff = float(brightness)/255
    frame = exposure.adjust_sigmoid(frame, cutoff, 8)
    return frame
