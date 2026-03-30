export async function scanNFC() {
  if ('NDEFReader' in window) {
    return scanWebNFC()
  }

  if (window.NativeNFC) {
    return scanNativeNFC()
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

