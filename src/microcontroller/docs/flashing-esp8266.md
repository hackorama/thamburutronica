Download from [Espriff](https://docs.espressif.com/projects/esp-at/en/release-v2.2.0.0_esp8266/AT_Binary_Lists/ESP8266_AT_binaries.html)

```shell
$ git clone https://github.com/espressif/esptool.git
$ cd esptool
$ pip install pyserial
```

```shell
$ cd ESP8266-IDF-AT_V2.2.1.0/ESP8266-AT-V2.2.1.0
$ cat download.config
--flash_mode dio --flash_freq 80m --flash_size 2MB 0x8000 partition_table/partition-table.bin 0x9000 ota_data_initial.bin 0x0 bootloader/bootloader.bin 0x10000 esp-at.bin 0xF0000 at_customize.bin 0xFC000 customized_partitions/client_ca.bin 0x106000 customized_partitions/mqtt_key.bin 0x104000 customized_partitions/mqtt_cert.bin 0x108000 customized_partitions/mqtt_ca.bin 0xF1000 customized_partitions/factory_param.bin 0xF8000 customized_partitions/client_cert.bin 0xFA000 customized_partitions/client_key.bin
$ python3 esptool.py  --port /dev/tty.usbserial-1410 write_flash @download.config
esptool /dev/tty.usbserial-1410 write_flash --flash_mode dio --flash_freq 80m --flash_size 2MB 0x8000 partition_table/partition-table.bin 0x9000 ota_data_initial.bin 0x0 bootloader/bootloader.bin 0x10000 esp-at.bin 0xF0000 at_customize.bin 0xFC000 customized_partitions/client_ca.bin 0x106000 customized_partitions/mqtt_key.bin 0x104000 customized_partitions/mqtt_cert.bin 0x108000 customized_partitions/mqtt_ca.bin 0xF1000 customized_partitions/factory_param.bin 0xF8000 customized_partitions/client_cert.bin 0xFA000 customized_partitions/client_key.bin
esptool.py v4.4-dev
Serial port /dev/tty.usbserial-1410
Connecting....
Detecting chip type... Unsupported detection protocol, switching and trying again...
Connecting...
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
Crystal is 26MHz
MAC: 2c:f4:32:8c:23:63
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Flash will be erased from 0x00008000 to 0x00008fff...
...
...
...
Hash of data verified.
Compressed 3368 bytes to 2526...
Wrote 3368 bytes (2526 compressed) at 0x000fa000 in 0.3 seconds (effective 89.7 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

```shell
$ python3 esptool.py  --port /dev/tty.usbserial-1410 chip_id
esptool.py v4.4-dev
Serial port /dev/tty.usbserial-1410
Connecting...
Detecting chip type... Unsupported detection protocol, switching and trying again...
Connecting...
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
Crystal is 26MHz
MAC: 2c:f4:32:8c:23:63
Stub is already running. No upload is necessary.
Chip ID: 0x008c2363
Hard resetting via RTS pin...
$
```
