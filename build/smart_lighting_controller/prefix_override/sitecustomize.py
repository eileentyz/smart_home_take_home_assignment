import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/eileen/Documents/GitHub/smart_home_take_home_assignment/install/smart_lighting_controller'
