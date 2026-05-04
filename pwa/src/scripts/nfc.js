export async function setup() {
	window.addEventListener("nfcDidScan", (e) => {
		display(`Read result: ${e.detail}`);
	});

	window.addEventListener("nfcWriteSuccess", (e) => {
		display(`Wrote successfully: ${e.detail}`);
	});

	window.addEventListener("nfcWriteError", (e) => {
		display(`Write error: ${e.detail}`);
	});

  // NFC Read
  document.querySelector("[data-nfc-scan]")?.addEventListener("click", () => { readNFC(); });

  // NFC Write
  document.querySelector("[data-nfc-write]")?.addEventListener("click", (e) => { 
    writeNFC(
      document.querySelector(`#${e.target.getAttribute('data-type-from')}`).value,
      document.querySelector(`#${e.target.getAttribute('data-payload-from')}`).value
    ) 
  });
  
  document.querySelectorAll("[data-nfc-write-explicit]").forEach(el => {
	el.addEventListener("click", (e) => {
		writeNFC(
			e.target.getAttribute('data-type'),
			e.target.getAttribute('data-payload')
		)
	})
  });

  document.querySelector("[data-nfc-write-explicit]").addEventListener("click", (e) => { 
    writeNFC(
      document.querySelector(`#${e.target.getAttribute('data-type-from')}`).value,
      document.querySelector(`#${e.target.getAttribute('data-payload-from')}`).value
    ) 
  });

}

/**
 * Displays the content in a <p> tag and appends it to <body>
 * @param {string} content - The text to display
 */
export function display(content) {
	const p = document.createElement("p");
	p.innerText = content;
	document.body.appendChild(p);
}

/**
 * Reads an NFC Tag
 */
export async function readNFC() {
  
	if ("NDEFReader" in window) {
    // Supports webNFC
		display("returning scanWebNFC()");
		return scanWebNFC();

	} else if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nfcScan) {
    // if iOS App
		display("webkit and webkit.messageHandlers.nfcScan detected");
		return window.webkit.messageHandlers.nfcScan.postMessage(null);

	} else {
    // Unavailable
		display("nfcScan bridge not available");
	}

  display("NFC not supported");
	throw new Error("NFC not supported");
}

export async function scanWebNFC() {
  display("scanWebNFC() running...");
	const reader = new NDEFReader();
	await reader.scan();

	return new Promise((resolve) => {
		reader.onreading = (event) => {
			display(event.message.records);
			resolve(event.message.records);
		};
	});
}


/**
 * Writes to an NFC Tag
 * @param {string} type - The NFC payload type (T = text, U = URL)
 * @param {string} content - The text or URL to write to the NFC
 */
export async function writeNFC(type, content) {
  // TODO - implement webNFC
  display(type);
  display(content);
  if (type != "song") {
	window.webkit.messageHandlers.nfcScan.postMessage({
		write: content || "Empty Content",
		type: type || "T",
	});
	} else {
		const songData = {
			"uuid" : crypto.randomUUID(),
			"cmd" : "song_write",
			"url" : content
		}
		display(JSON.stringify(songData));
		window.webkit.messageHandlers.nfcScan.postMessage({
			write: songData,
			type: "T",
		});
	}
}