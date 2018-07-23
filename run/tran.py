#idx = [0] * 256
#c=0
#for i in range(0,16):
#        if i<8:
#                begin_idx = 256-32*i
#        else:
#                begin_idx = 256-32*(i-8) - 8
#
#        for j in range(0,8):
#                c = begin_idx - j
#                idx[c-1] = i*16 + j
#        for j in range(8,16):
#                c = begin_idx- 8 - j
#                idx[c-1] = i*16 + j
#
#print idx
bat_tmp = [0] * 256
idx = [0] * 256
c=0
for i in range(0,16):
    if i<8:
        begin_idx = 256-32*i
    else:
        begin_idx = 256-32*(i-8) - 8

    for j in range(0,8):
        c = begin_idx - j
        idx[c-1] = i*16 + j
    for j in range(8,16):
        c = begin_idx- 8 - j
        idx[c-1] = i*16 + j
print idx

