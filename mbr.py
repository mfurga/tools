#!/usr/bin/env python3
# Master Boot Record

import sys

PARTITION_TYPE = {
  0x00: "Empty",
  0x01: "FAT12, CHS",
  0x04: "FAT16, 16-32 MB, CHS",
  0x05: "Microsoft Extended, CHS",
  0x06: "FAT16, 32 MB-2GB, CHS",
  0x07: "NTFS",
  0x0b: "FAT32, CHS",
  0x0c: "FAT32, LBA",
  0x0e: "FAT16, 32 MB-2GB, LBA",
  0x0f: "Microsoft Extended, LBA",
  0x11: "Hidden Fat12, CHS",
  0x14: "Hidden FAT16, 16-32 MB, CHS",
  0x16: "Hidden FAT16, 32 MB-2GB, CHS",
  0x1b: "Hidden FAT32, CHS",
  0x1c: "Hidden FAT32, LBA",
  0x1e: "Hidden FAT16, 32 MB-2GB, LBA",
  0x27: "Windows Recovery Environment",
  0x42: "Microsoft MBR, Dynamic Disk",
  0x82: "Solaris x86 -or- Linux Swap",
  0x83: "Linux",
  0x84: "Hibernation",
  0x85: "Linux Extended",
  0x86: "NTFS Volume Set",
  0x87: "NTFS Volume SET",
  0xa0: "Hibernation",
  0xa1: "Hibernation",
  0xa5: "FreeBSD",
  0xa6: "OpenBSD",
  0xa8: "Mac OSX",
  0xa9: "NetBSD",
  0xab: "Mac OSX Boot",
  0xb7: "BSDI",
  0xb8: "BSDI swap",
  0xdb: "Recovery Partition",
  0xde: "Dell Diagnostic Partition",
  0xee: "EFI GPT Disk",
  0xef: "EFI System Partition",
  0xfb: "Vmware File System",
  0xfc: "Vmware swap"
}

def bytes_to_human(b):
  units = ["B", "KiB", "MiB", "GiB", "TiB"]
  i = 0
  while b > 1024:
    i += 1
    b /= 1024
  return f"{b:.4f} {units[i]}"

def partition_status(status):
  s = "?"
  if status == 0:
    s = "Inactive"
  elif status <= 0x7f:
    s = "Invalid"
  elif (status >> 7) & 1:
    s = "Bootable"
  return s

def chs_to_lba(cylinder, head, sector):
  # LBA -> CHS
  # 0 -> (0, 0, 1)
  # 1 -> (0, 0, 2)
  # 62 -> (0, 0, 63)
  # 63 -> (0, 1, 1)
  # 64 -> (0, 1, 2)
  # 945 -> (0, 15, 1)
  # 1007 -> (0, 15, 63)
  # 1008 -> (1, 0, 1)
  H = 16  # 0 - 15
  S = 63  # 1 - 63, 6 bits but counting from 1 ;)
  C = 1024
  return cylinder * H * S + head * S + (sector - 1)

def lba_to_chs(lba):
  H = 16
  S = 63
  C = 1024
  s = lba % S + 1
  h = (lba // S) % H
  c = lba // (S * H)
  return (c, h, s)

def partition_table_info(num, data):
  assert len(data) == 16

  status = int.from_bytes(data[0:1], "little")
  start_chs = int.from_bytes(data[1:4], "little")
  partition_type = int.from_bytes(data[4:5], "little")
  end_chs = int.from_bytes(data[5:8], "little")
  lba = int.from_bytes(data[8:12], "little")
  sectors = int.from_bytes(data[12:16], "little")

  start_chs_head = start_chs & 0xff
  start_chs_sector = (start_chs >> 8) & 0b111111
  start_chs_cylinder = (((start_chs >> 14) & 0b11) << 8) | (start_chs >> 16)

  end_chs_head = end_chs & 0xff
  end_chs_sector = (end_chs >> 8) & 0b111111
  end_chs_cylinder = (((end_chs >> 14) & 0b11) << 8) | (end_chs >> 16)

  print(f"=== Partition table #{num}:")

  if partition_type == 0:
    print(f"    Partition type: {PARTITION_TYPE[partition_type]} (0x{partition_type:02x})")
    return

  print(f"    Status: {partition_status(status)} (0x{status:02x})")
  print(f"    Partition type: {PARTITION_TYPE[partition_type]} (0x{partition_type:02x})")
  print(f"    CHS address of first sector: 0x{start_chs:06x}")
  print(f"        cylinder: {start_chs_cylinder}")
  print(f"        head: {start_chs_head}")
  print(f"        sector: {start_chs_sector}")
  print(f"    CHS address of last sector: 0x{end_chs:06x}")
  print(f"        cylinder: {end_chs_cylinder}")
  print(f"        head: {end_chs_head}")
  print(f"        sector: {end_chs_sector}")
  print(f"    LBA address of first sector: 0x{lba:08x}")
  print(f"    Number of sectors: {sectors} ({bytes_to_human(sectors * 512)})")
  print()

def main(file):
  with open(file, "rb") as f:
    data = f.read()

  assert len(data) == 512

  signature = int.from_bytes(data[440:444], "little")
  print(f"Disk signature 0x{signature:08x}")

  partition1 = data[510 - 16 * 4:510 - 16 * 3]
  partition2 = data[510 - 16 * 3:510 - 16 * 2]
  partition3 = data[510 - 16 * 2:510 - 16 * 1]
  partition4 = data[510 - 16 * 1:510 - 16 * 0]

  partition_table_info(1, partition1)
  partition_table_info(2, partition2)
  partition_table_info(3, partition3)
  partition_table_info(4, partition4)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <MBR boot sector>")
    sys.exit(1)
  main(sys.argv[1])

