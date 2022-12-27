/**
 * The web UI module
 *
 * Checks device connection status and sends the chord clicks to server
 */
const ERROR_COLOR = "#e53935";
const CHORD_COLOR = "#add8e6";
const CHORD_ACTIVE_COLOR = "#9d3ba0";
const CHORD_DISABLED_COLOR = "#aaaaaa";
const CHORD_BLINK_COLOR = "#eeeeee";

let chords: HTMLCollectionOf<HTMLSpanElement>;
let connected: boolean = false;

function start() {
  chords = document.getElementsByTagName("span");
  for (let i = 0; i < chords.length; i++) {
    chords[i].onclick = chordClick;
  }
  ping();
}

function settings() {
  stat();
}

async function stat() {
  console.log("Getting system status ...");
  let system_elem = document.getElementById("system");
  if (!system_elem) {
    return;
  }
  system_elem.innerHTML = "Checking device   .";
  let status = null;
  fetch("/device/diag")
    .then((response) => response.text())
    .then((data) => (status = JSON.parse(data))) // Parse to remove quotes
    .catch(function (ex) {
      status = "error";
      console.log("status = %s", status);
    });
  let c = 0;
  while (!status) {
    console.log("status = %s", status);
    system_elem.innerHTML =
      c % 2 ? "Checking device . ." : "Checking device ...";
    await new Promise((r) => setTimeout(r, 1000));
    c++;
  }
  console.log("status = %s", status);
  system_elem.innerHTML = status;
}

function chordClick(this: any) {
  if (connected === false) {
    return;
  }
  hideAlerts();
  // Toggle clicked chord color
  if (this.getAttribute("status") == "clicked") {
    this.setAttribute("status", "");
    this.style.backgroundColor = CHORD_COLOR;
    setChord(0);
  } else {
    this.setAttribute("status", "clicked");
    this.style.backgroundColor = CHORD_ACTIVE_COLOR;
    setChord(this.id);
  }
  // Reset rest of the chord colors
  for (let i = 0; i < chords.length; i++) {
    if (chords[i].id != this.id) {
      chords[i].style.backgroundColor = CHORD_COLOR;
      chords[i].setAttribute("status", "");
    }
  }
}

function hideAlerts() {
  let alert_elem = document.getElementById("header");
  if (alert_elem) {
    alert_elem.style.display = "none";
  }
}

function delay(time: number) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

function setChordColors(color: string) {
  for (let i = 0; i < chords.length; i++) {
    chords[i].style.backgroundColor = color;
  }
}

async function ping() {
  console.log("ping ...");
  let alert_elem = document.getElementById("header");
  if (!alert_elem) {
    return;
  }
  alert_elem.textContent = "Connecting ...";
  let pong = null;
  fetch("/device/ping")
    .then(function (response) {
      pong = response.status;
    })
    .catch(function (ex) {
      pong = "error";
      console.log("ping = %s", pong);
    });
  let c = 0;
  while (!pong) {
    console.log("ping = %s", pong);
    for (let i = 0; i < chords.length; i++) {
      setChordColors(c % 2 ? CHORD_BLINK_COLOR : CHORD_DISABLED_COLOR);
    }
    await new Promise((r) => setTimeout(r, 1000));
    c++;
  }
  console.log("ping = %s", pong);
  setChordColors(CHORD_DISABLED_COLOR);
  if (pong == 200) {
    connected = true;
    alert_elem.textContent = "Touch chords to play";
    setChordColors(CHORD_COLOR);
  } else {
    alert_elem.innerHTML =
      "Check connection and <a href='index.html'>retry</a>";
  }
}

async function setChord(chord: number) {
  let response = await fetch("/chord/" + chord);
  let data = await response.json();
  console.log("chord set %s = %s", chord, data);
}
