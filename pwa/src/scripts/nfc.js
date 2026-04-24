export async function setup() {
  window.addEventListener("nfcDidScan", e => { nfcDidScan(e) });
  
}


export async function scanNFC() {
  if ('NDEFReader' in window) {
    const p = document.createElement('p');
    p.innerText = "returning scanWebNFC()";
    document.body.appendChild(p);
    return scanWebNFC()
  } else if ( window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nfcScan) {
    const p = document.createElement('p');
    p.innerText = "webkit and webkit.messageHandlers.nfcScan detected";
    document.body.appendChild(p);
    return window.webkit.messageHandlers.nfcScan.postMessage(null);
  } else {
      const p = document.createElement('p');
      p.innerText = "nfcScan bridge not available";
      document.body.appendChild(p);
      console.log("nfcScan bridge not available");
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


// Called when NFC Data Received
export async function nfcDidScan(data) {
  const p = document.createElement('p');
  p.innerText = data;
  document.body.appendChild(p);
}


