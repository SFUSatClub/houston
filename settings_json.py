import json

""" Key: description of port/board. Value: the true device path """
board_names = {
    'Use Manual Entry'                      : 'use_man',
    'Launchpad - tty.usbserial-TIXRGQDLB'   : '/dev/tty.usbserial-TIXRGQDLB',
    '0.4C - cu.usbserial-A700eYE7'          : '/dev/cu.usbserial-A700eYE7',
    '0.4x - tty.usbserial-A50285BI'         : '/dev/tty.usbserial-A50285BI',
    '0.5A - cu.usbserial-DN02I8UQ'          : '/dev/cu.usbserial-DN02I8UQ',
    'Windows - COM7'                        : 'COM7',
    'Internal Simulator'                    : 'simulator'
    
}


settings_json = json.dumps([
    {'type': 'title',
    'title': ''},
    {'type': 'title',
    'title': 'Select a serial port or change to "Use Manual Entry and enter a string"'},
     {'type': 'options',
    'title': 'UART Port',
    'desc': 'Location of the USB-Serial device, in /dev (Mac/Linux) or COMx (Windows)',
    'section': 'houston_settings',
    'key':'uart_options',
    'options': list(board_names.keys())},
    {'type': 'string',
    'title': 'UART Port - Manual Entry',
    'desc': "Enter device location ex: /dev/tty.usbserial123 ",
    'section': 'houston_settings',
    'key':'uart_string'},

])


