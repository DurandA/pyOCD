# pyOCD debugger
# Copyright (c) 2006-2018 Arm Limited
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ..family.target_kinetis import Kinetis
from ..family.flash_kinetis import Flash_Kinetis
from ...core.memory_map import (FlashRegion, RamRegion, MemoryMap)
from ...debug.svd import SVDFile
import logging

SIM_FCFG1 = 0x4004804C
SIM_FCFG2 = 0x40048050
SIM_FCFG2_PFLSH = (1 << 23)

log = logging.getLogger("target.k22fa12")

FLASH_ALGO = {
    'load_address' : 0x20000000,
    'instructions' : [
    0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
    0xb510483e, 0x5120f24c, 0xf64d81c1, 0x81c11128, 0xf0218801, 0x80010101, 0x78414839, 0x0160f001,
    0xbf0c2940, 0x21002101, 0x444a4a36, 0xb1397011, 0xf0217841, 0x70410160, 0xf0117841, 0xd1fb0f60,
    0x44484831, 0xf864f000, 0xbf182800, 0xbd102001, 0x4448482c, 0xb1587800, 0x78414829, 0x0160f021,
    0x0140f041, 0x78417041, 0x0160f001, 0xd1fa2940, 0x47702000, 0xb5104824, 0x44484924, 0xf891f000,
    0xbf182800, 0x2100bd10, 0xe8bd481f, 0x44484010, 0xb958f000, 0x4c1cb570, 0x444c4605, 0x4b1b4601,
    0x68e24620, 0xf8b6f000, 0xbf182800, 0x2300bd70, 0x68e24629, 0x4070e8bd, 0x44484813, 0xb94cf000,
    0x460cb570, 0x4606460b, 0x480f4601, 0x4615b084, 0xf0004448, 0x2800f8eb, 0xb004bf1c, 0x2000bd70,
    0xe9cd2101, 0x90021000, 0x462b4807, 0x46314622, 0xf0004448, 0xb004f97f, 0x0000bd70, 0x40052000,
    0x4007e000, 0x00000004, 0x00000008, 0x6b65666b, 0xbf042800, 0x47702004, 0x6cc949ea, 0x6103f3c1,
    0xbf08290f, 0x1180f44f, 0x4ae7bf1f, 0xf832447a, 0x02891011, 0xe9c02200, 0x21022100, 0x61426081,
    0x618202c9, 0x1203e9c0, 0x52a0f04f, 0x2108e9c0, 0x47702000, 0xbf0e2800, 0x61012004, 0x47702000,
    0x48da4602, 0x49d96840, 0x0070f440, 0x47706048, 0x217048d7, 0x21807001, 0x78017001, 0x0f80f011,
    0x7800d0fb, 0x0f20f010, 0x2067bf1c, 0xf0104770, 0xbf1c0f10, 0x47702068, 0x0001f010, 0x2069bf18,
    0x28004770, 0x2004bf04, 0xb5104770, 0x4ac84604, 0x403bf06f, 0x48c76050, 0xbf144281, 0x2000206b,
    0xbf182800, 0x4620bd10, 0xffd2f7ff, 0x46204603, 0xffc6f7ff, 0xbd104618, 0xbf042800, 0x47702004,
    0x60532300, 0x60d36093, 0x61536113, 0x61d36193, 0x68c16011, 0xe9d06051, 0xfbb11001, 0x6090f0f0,
    0x21102008, 0x0103e9c2, 0x1005e9c2, 0x61d02004, 0x47702000, 0x4df0e92d, 0x4615b088, 0x460c4698,
    0x466a4682, 0xffd8f7ff, 0x4621462a, 0x9b044650, 0xf931f000, 0xbf1c0007, 0xe8bdb008, 0xe9dd8df0,
    0x19604600, 0xfbb51e45, 0xfb06f0f6, 0xb1205010, 0xf0f6fbb5, 0x43701c40, 0x42ac1e45, 0xf8dfbf98,
    0xd81cb270, 0x407ff024, 0x6010f040, 0x0004f8cb, 0x45804898, 0x206bbf14, 0x28002000, 0xb008bf1c,
    0x8df0e8bd, 0xf7ff4650, 0x4607ff73, 0x0010f8da, 0xbf182800, 0xb9174780, 0x42ac4434, 0x4650d9e2,
    0xff5ef7ff, 0x4638b008, 0x8df0e8bd, 0xbf042a00, 0x47702004, 0x45f0e92d, 0x4614b089, 0x460d461e,
    0x466a4680, 0xff88f7ff, 0x46294632, 0x9b034640, 0xf8e1f000, 0xbf1c0007, 0xe8bdb009, 0x9d0085f0,
    0xbf182e00, 0xa1e8f8df, 0xf854d025, 0xf8ca0b04, 0x98030008, 0xbf042804, 0x407ff025, 0x60c0f040,
    0x2808d009, 0xf854d109, 0xf8ca0b04, 0xf025000c, 0xf040407f, 0xf8ca60e0, 0x46400004, 0xff28f7ff,
    0x1010f8d8, 0x29004607, 0x4788bf18, 0x9803b91f, 0x1a364405, 0x4640d1d9, 0xff12f7ff, 0x4638b009,
    0x85f0e8bd, 0xbf042800, 0x47702004, 0xea424a62, 0x4a5f4101, 0xe70b6051, 0x4dffe92d, 0x4614b088,
    0x460d469a, 0x9808466a, 0xff36f7ff, 0x46294622, 0x98089b05, 0xf88ff000, 0xbf1c2800, 0xe8bdb00c,
    0x466a8df0, 0x98084629, 0xff26f7ff, 0xf8dd9e00, 0x42708008, 0x0100f1c8, 0x42474008, 0xbf0842b7,
    0x2c004447, 0xf8dfbf18, 0xd01fb128, 0x42a51bbd, 0x4625bf88, 0xf0269805, 0xfbb5417f, 0xf041f0f0,
    0xf8cb7180, 0x04001004, 0x200aea40, 0x00fff040, 0x0008f8cb, 0xf7ff9808, 0x2800fecb, 0xb00cbf1c,
    0x8df0e8bd, 0x442e1b64, 0xd1df4447, 0x2000b00c, 0x8df0e8bd, 0xbf042b00, 0x47702004, 0x4dffe92d,
    0x4616b088, 0x7a14e9dd, 0x460c461d, 0xf8dd466a, 0x98088058, 0xfee0f7ff, 0x3007e9dd, 0x46214632,
    0xf839f000, 0xbf1c2800, 0xe8bdb00c, 0x9c008df0, 0xbf042e00, 0xe8bdb00c, 0xf8df8df0, 0xf06fb094,
    0xea40407f, 0xf0246707, 0xf040407f, 0xf8cb7000, 0xf8cb0004, 0x68287008, 0x000cf8cb, 0xf7ff9808,
    0xb168fe87, 0x0f00f1ba, 0xf8cabf18, 0xf1b84000, 0xbf1c0f00, 0xf8c82100, 0xb00c1000, 0x8df0e8bd,
    0x1a769907, 0x0103f021, 0x9907440d, 0xd1da440c, 0xe8bdb00c, 0x28008df0, 0x2004bf04, 0x1e5b4770,
    0xbf0e4219, 0x2065421a, 0x68034770, 0xd806428b, 0x44116840, 0x42884418, 0x2000bf24, 0x20664770,
    0x00004770, 0x40048000, 0x000003b4, 0x4001f000, 0x40020000, 0x6b65666b, 0x4000ffff, 0x40020004,
    0x40020010, 0x00100008, 0x00200018, 0x00400030, 0x00800060, 0x010000c0, 0x02000180, 0x04000300,
    0x00000600, 0x00000000, 0x00000000,
    ],

    'pc_init' : 0x20000021,
    'pc_unInit': 0x20000071,
    'pc_program_page': 0x200000E1,
    'pc_erase_sector': 0x200000B5,
    'pc_eraseAll' : 0x20000095,

    'static_base' : 0x20000000 + 0x00000020 + 0x00000504,
    'begin_stack' : 0x20000000 + 0x00000800,
    'begin_data' : 0x20000000 + 0x00000A00,
    'page_size' : 0x00000200,
    'analyzer_supported' : True,
    'analyzer_address' : 0x1ffff000,  # Analyzer 0x1ffff000..0x1ffff600
    'page_buffers' : [0x20003000, 0x20004000],   # Enable double buffering
    'min_program_length' : 8,
};

class K22FA12(Kinetis):

    # 1MB flash with 4kB sectors, 128kB RAM
    memoryMap = MemoryMap(
        FlashRegion(    start=0,           length=0x100000,     blocksize=0x1000, is_boot_memory=True,
            algo=FLASH_ALGO, flash_class=Flash_Kinetis),
        RamRegion(      start=0x1fff0000,  length=0x20000)
        )

    def __init__(self, link):
        super(K22FA12, self).__init__(link, self.memoryMap)
        self._svd_location = SVDFile(vendor="Freescale", filename="MK22FA12.svd", is_local=False)

    def create_init_sequence(self):
        seq = super(K22FA12, self).create_init_sequence()

        # Modify the memory map for FlexNVM devices.
        seq.insert_before('create_cores',
            ('fixup_memory_map', self.fixup_memory_map)
            )

        return seq

    def fixup_memory_map(self):
        # If the device has FlexNVM, then it has half-sized program flash.
        fcfg2 = self.dp.aps[0].read32(SIM_FCFG2)
        if (fcfg2 & SIM_FCFG2_PFLSH) == 0:
            log.debug("%s: device has FlexNVM", self.part_number)
            rgn = self.memory_map.get_region_for_address(0)
            rgn._end = 0x7ffff
        else:
            log.debug("%s: device does not have FlexNVM", self.part_number)

