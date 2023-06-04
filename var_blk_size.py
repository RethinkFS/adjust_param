import os
SECT_SIZE = [128, 512, 1024, 2048, 4096]
ZONE_SIZE = [16, 32, 64]
# create a nullblk ,params : <sect size (B)> <zone size (MB)> <nr conv zones> <nr seq zones>
NULLBLK_ZONED_SH = "sudo ../plugin/aquafs/tests/nullblk/nullblk-zoned.sh"
# delete a nullblk ,params : 
NULLBLK_ZONED_REMOVE_SH = "sudo ../plugin/aquafs/tests/nullblk/nullblk-zoned-remove.sh"

NULLBLK_NUM = 1

def create_null_blk(sect_size, zone_size,conv_zones = 0, seq_zones = 64, num=NULLBLK_NUM):
    execute_str = NULLBLK_ZONED_SH + " " + str(sect_size) + " " + str(zone_size) + " " + str(conv_zones) + " " + str(seq_zones)
    for _ in range(num):
        os.system(execute_str)

def remove_null_blk(num=NULLBLK_NUM):
    execute_str = NULLBLK_ZONED_REMOVE_SH
    for i in range(num):
        execute = execute_str + " " + str(i)
        os.system(execute)