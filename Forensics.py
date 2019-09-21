# import data and seperate bootsector

data = open('image.dat','rb').read()
#print data
hex_data = ["{:02x}".format(ord(c)) for c in data]
#print(hex_data)
hex_BootSector = hex_data[0:512]

#print(hex_BootSector)

# method to fix little endian
def read_hex(data, offset, length):
    result = ''
    while length >= 1:
        length = length - 1
        result += data[offset + length]
    return result


# read fat tables
# TODO parse data from BS to avoid hard coding
hex_fat1 = hex_data[1 * 512:10 * 512]
hex_fat2 = hex_data[10 * 512:19 * 512]

#handle 12bit little endian
def read_12bit(data):
    temp=[]
    for x in range(1,len(data),3):
        tmp=list(data[x])
        data[x-1]=tmp[1]+data[x-1]
        data[x+1]=data[x+1]+tmp[0]

    for x in range(0, len(data)):
        if (len(data[x])>2):
            temp.append(data[x])
    return temp

hex12_fat1=read_12bit(hex_fat1)
hex12_fat2=read_12bit(hex_fat2)
# print hex12_fat1
# print hex12_fat2

#read root dir
#TODO same as previous
hex_root_raw=hex_data[9728:16896]
#print hex_root_raw

#process root dir
hex_root=[]
entries=(int(read_hex(hex_BootSector,17,2),16))

for x in range(0,entries):
    tmp=hex_root_raw[x*32:x*32+32]
    hex_root.append(tmp)
#print hex_root

#collect relevant information
filesizes=[]
for x in hex_root:
    name=read_hex(x,0,11).decode('hex')
    name=name[::-1]
    size=read_hex(x,28,4)
    first_cluster=read_hex(x,26,2)
    filesizes.append([first_cluster,size,name])

data_offset=16896
#print relevant entries
for x in filesizes:
    if x[0]!= '0000' and x[1]!= '00000000' and x[1]!= 'ffffffff':
        f=open(x[2],"w+")
        index2=int(x[0],16)
        offset=index2*512
        start_cluster=data_offset+offset
        for y in range(start_cluster,start_cluster+int(x[1],16)):
            f.write(hex_data[y].decode("hex"))
#TODO make sense of the files


#hexfile located from offset 0x24600
#zip header 0x04034b50
#EOF is marked by 0x06054b50 found at address 0x24dd7
start_zip=''
end_zip=''
for x in range(0,len(hex_data)-4):
    temp=read_hex(hex_data,x,4)
    if temp=='04034b50':
        start_zip=x

for y in range(start_zip,len(hex_data)-4):
    temp=read_hex(hex_data,y,4)
    if temp=='06054b50':
        end_zip=y
print start_zip
print end_zip
print(int(str(start_cluster),16))
print(int(str(end_zip),16))

#TODO parse and output zip file