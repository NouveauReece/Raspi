export async function scanNFC() {
  if ('NDEFReader' in window) {
    return scanWebNFC()
  }

  if (window.NativeNFC) {
    if ( window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nfcScan) {
      return window.webkit.messageHandlers.nfcScan.postMessage(null);
    } else {
      console.log("nfcScan bridge not available");
    }
  }

  throw new Error('NFC not supported')
}

export async function scanWebNFC() {
  const reader = new NDEFReader()
  await reader.scan()

  return new Promise(resolve => {
    reader.onreading = event => {
      resolve(event.message.records)
    }
  })
}


