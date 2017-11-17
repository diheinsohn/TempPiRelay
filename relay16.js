 mask = 'use strict';

class Relay16 {

  constructor()
  {
    let USB_VID = 0x0416;
    let USB_PID = 0x5020;

    let HID = require('node-hid');

    // Generated by mapRelays()
    this.relayBitmap = [128, 256, 64, 512, 32, 1024, 16, 2048, 8, 4096, 4, 8192, 2, 16384, 1, 32768];

    console.log('Detected devices:', HID.devices(USB_VID, USB_PID));
    this.hid = new HID.HID(USB_VID, USB_PID);
  }

  state()
  {
    console.log(readmask);
  }

  set(id, state)
  {
    if (typeof id !== 'number') {
      throw `Invalid relay ID type: ${id}`;
    }
    if (id < 0 || id > 15) {
      throw `Invalid relay ID: ${id}`;
    }
    if (typeof state !== 'boolean') {
      throw `Invalid state: ${state}`;
    }

    return this.read()
      .then(readmask => {
        let bit = Math.pow(2, id);

        // Map the read mask into the write mask
        let mask = 0;
        for (let i = 0; i < 16; i++) {
          if (readmask & this.relayBitmap[i]) {
            mask = mask | Math.pow(2, i);
          }
        }

        if (state) {
    	   mask = mask | bit;
        } else {	
	   mask = mask & ~bit;	   
        }
        return this.write(mask);
      });
  }

  read()

  {
    return new Promise((resolve, reject) => {
      let readCmd = [
        0xD2, 0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x48, 0x49, 0x44,
        0x43, 0x80, 0x02, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
        0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
        0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
        0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC
      ];
      this.hid.write(readCmd);

      this.hid.read((err, data) => {
        if (err) {
	  this.reset();
          return reject('hid read error: ${err}');
        }

        let arr16 = new Uint16Array(1);
        let arr8 = new Uint8Array(arr16.buffer);
        arr8[0] = data[2];
        arr8[1] = data[3];

        let mask = arr16[0];
        return resolve(mask);
      });
    });
  }

  reset()
  {
    let resetCmd = [
      0x71, 0x0E, 0x71, 0x00, 0x00, 0x00, 0x11, 0x11, 0x00, 0x00, 0x48, 0x49, 0x44,
      0x43, 0x2A, 0x02, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
      0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
      0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
      0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC
    ];
    this.hid.write(resetCmd);
    return Promise.resolve();
  }

  write(mask)
  {
    if (typeof mask !== 'number' || mask < 0 || mask > 0xFFFF) {
      this.reset();
      throw `Invalid write mask: ${mask}`;
    }

    let writeCmd = [
      0xC3, 0x0E, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x48, 0x49, 0x44,
      0x43, 0xEE, 0x01, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
      0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
      0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC,
      0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC
    ];

    let arr16 = new Uint16Array(1);
    let arr8 = new Uint8Array(arr16.buffer);
    arr16[0] = mask;

    writeCmd[2] = arr8[0];
    writeCmd[3] = arr8[1];

    let addCommandChecksum = cmd => {
      let size = cmd[1];
      let checksum = cmd.slice(0, size).reduce((a, b) => a + b, 0);

      let arr32 = new Uint32Array(1);
      let arr8 = new Uint8Array(arr32.buffer);
      arr32[0] = checksum;

      for (let i = 0; i < 4; i++) {
        cmd[size + i] = arr8[i];
      }
      return cmd;
    };

    this.hid.write(addCommandChecksum(writeCmd));
    return Promise.resolve();
  }
}

module.exports = Relay16;
