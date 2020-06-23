import gi
import time

import usb.core
import usb.util


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib,Gdk
from gi.repository import GdkPixbuf

#Look for the USB device using vendor ID and Prouct ID 
dev = usb.core.find(idVendor=0x0483,idProduct=0x575a)

# If USB device is not found then raise exception
if dev is None :
  raise ValueError('Device not found')

# Detach the kernel driver in case it's stuck in use by other program 
if dev.is_kernel_driver_active(0):
  reattach = True
  dev.detach_kernel_driver(0)

# Find the configuration interface 1
cfg = usb.util.find_descriptor(dev,bConfigurationValue=1)
# Use conifguration interace 1
cfg.set()

# 2 bytes buffer , 1st indicating LED : 0-> White, 1->Blue , 2->Red, 3->Green . 2nd indicating LED status 0->Off, 1->On
outBuffer = ['0','0']

# LED to number mapping Dictionary 
buttonMapping = { 'white' : '0' ,'blue':'1','red':'2' , 'green' : '3'}


class Custom_USB_HID_Demo(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="USB CUSTOM HID DEMO")
        self.set_border_width(10)

	grid = Gtk.Table(4,4,True)
	self.add(grid)
	
	buttons={}	# buttons dict
	self.pixbufs={} # pixbufs for images dict
	self.images={}  # image widgets dicts

	# create 4 buttons and connect toggle event to on_button_toggle function
	for b in ['red', 'white' , 'blue' , 'green']:
          buttons[b]=Gtk.ToggleButton(b.upper())
          buttons[b].connect("toggled", self.on_button_toggled,b)

	
	# returns list [imageOFF, imageON]
	self.pixbufs['red']   = self.getImageCouple('red')
	self.pixbufs['white'] = self.getImageCouple('white')
	self.pixbufs['blue']  = self.getImageCouple('blue')
	self.pixbufs['green'] = self.getImageCouple('green')
	self.pixbufs['yellow'] = self.getImageCouple('yellow')

	# create Image dict containing 2 image instances , left LEDs and Right LEDs , initialized with pixbuf images
	self.images['red']= Gtk.Image.new_from_pixbuf(self.pixbufs['red'][0]) 
	self.images['white']= Gtk.Image.new_from_pixbuf(self.pixbufs['white'][0])
	self.images['blue']= Gtk.Image.new_from_pixbuf(self.pixbufs['blue'][0]) 
	self.images['green']= Gtk.Image.new_from_pixbuf(self.pixbufs['green'][0])
	self.images['yellow1']= Gtk.Image.new_from_pixbuf(self.pixbufs['yellow'][0])
	self.images['yellow2']= Gtk.Image.new_from_pixbuf(self.pixbufs['yellow'][0])

        # attach the buttons to the table layout 
	grid.attach(buttons['white'],0,1,0,1)
	grid.attach(buttons['blue'],0,1,1,2)
	grid.attach(buttons['red'],0,1,2,3)
	grid.attach(buttons['green'],0,1,3,4)

	# attach the images to the tabel layout . LEFT LEDs
	grid.attach(self.images['white'],1,2,0,1)
	grid.attach(self.images['blue'],1,2,1,2)
	grid.attach(self.images['red'],1,2,2,3)
	grid.attach(self.images['green'],1,2,3,4)

		
	# attach the images to the tabel layout . RIGHT LEDs
	grid.attach(self.images['yellow1'],3,4,0,1)
	grid.attach(self.images['yellow2'],3,4,3,4)


	#self.toggle=False
	# Call to the function do_puse each 100ms
	self.timeout_id = GLib.timeout_add(100,self.do_pulse)


    #Load LED images to the PixBuf object insrances
    def getImageCouple(self,name):
	imageON = GdkPixbuf.Pixbuf.new_from_file(name+"_on.png")
	imageOFF = GdkPixbuf.Pixbuf.new_from_file(name+"_off.png")
	imageON = imageON.scale_simple(20,20,GdkPixbuf.InterpType.NEAREST)
	imageOFF = imageOFF.scale_simple(20,20,GdkPixbuf.InterpType.NEAREST)
	return [imageOFF,imageON]

    #Toggle LEDs when buttons are clicked
    def on_button_toggled(self, button,name):
	#if ('' in button.get_label()) :
        if button.get_active():
  	    self.images[name].set_from_pixbuf(self.pixbufs[name][1])
	    outBuffer[0]=buttonMapping[name]
	    outBuffer[1]='0'
        else:
  	    self.images[name].set_from_pixbuf(self.pixbufs[name][0])
	    outBuffer[0]=buttonMapping[name]
	    outBuffer[1]='1'
	# sending buffer to the usb device :exp :  00 , 01 , 21 ...
	dev.write(0x01,''.join(outBuffer),100)
    

    def do_pulse(self):

      #Read 2 bytes from IN Endpoint , with 100ms timeout
      ret = dev.read(0x81,2, 100)
     
      # Toggle Yellow LED 1  depending on the 1st byte stat :
      if chr(ret[0]) == '0':
	self.images['yellow1'].set_from_pixbuf(self.pixbufs['yellow'][0])
      else :
	self.images['yellow1'].set_from_pixbuf(self.pixbufs['yellow'][1])

      # Toggle Yellow LED 2  depending on the 2nd byte stat :
      if chr(ret[1]) == '0':
	self.images['yellow2'].set_from_pixbuf(self.pixbufs['yellow'][0])
      else :
	self.images['yellow2'].set_from_pixbuf(self.pixbufs['yellow'][1])

      # must return True to keep pulsing
      return True


win = Custom_USB_HID_Demo()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
