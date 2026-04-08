export async function scanNFC() {
  if ('NDEFReader' in window) {
    return scanWebNFC()
  }

  if (window.NativeNFC) {
    if ( window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nfcScan) {
      const p = document.createElement('p');
      p.innerText = "webkit and webkit.messageHandlers.nfcScan detected";
      document.body.appendChild(p);
      return window.webkit.messageHandlers.nfcScan.postMessage(null);
    } else {
      console.log("nfcScan bridge not available");
    }
  }

  throw new Error('NFC not supported')
}

export async function scanWebNFC() {
  const reader = new NDEFReader()
  const p = document.createElement('p');
  p.innerText = "scanWebNFC() running...";
  document.body.appendChild(p);
  await reader.scan()

  return new Promise(resolve => {
    reader.onreading = event => {
      const p = document.createElement('p');
      p.innerText = event.message.records;
      document.body.appendChild(p);
      resolve(event.message.records);
    }
  })
}


