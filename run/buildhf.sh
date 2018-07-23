#!/bin/sh
find ext/ protocol/ -iname "*.py" -exec cython {} \;
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o protocol/protocol_cancrc.so protocol/protocol_cancrc.c
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o protocol/protocol_can.so protocol/protocol_can.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o protocol/protocol_rs485.so protocol/protocol_rs485.c
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o protocol/protocol_rs.so protocol/protocol_rs.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/vcan/hf_vcan.so ext/vcan/hf_vcan.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/vcan/mcp2515.so ext/vcan/mcp2515.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/vcan/mcp2515_context.so ext/vcan/mcp2515_context.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/vcan/rs485.so ext/rs485/rs485.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/vcan/rs232.so ext/rs232/rs232.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/main/hf_main.so ext/main/hf_main.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/io/hf_io.so ext/io/hf_io.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/data_uploader/DataUploader.so ext/data_uploader/DataUploader.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/iic/iic.so ext/iic/iic.c
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o ext/control/hf_control.so ext/control/hf_control.c
find ext/ protocol/ -iname "*.so" -exec strip {} \;
