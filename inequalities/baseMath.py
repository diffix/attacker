import math
import pprint
pp = pprint.PrettyPrinter(indent=4)

# To find larger snapped width than given width:

def largerSnappedWidth(base, wid):
    print("Larger snapped width {wid}, base {base}")
    logged = math.log(wid,base)
    print(f"  logged {logged}")

low = 48.23
high = 71.8
width = high-low
base = 10
largerSnappedWidth(base,width)
