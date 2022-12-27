"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
/**
 * The web UI module
 *
 * Checks device connection status and sends the chord clicks to server
 */
var ERROR_COLOR = "#e53935";
var CHORD_COLOR = "#add8e6";
var CHORD_ACTIVE_COLOR = "#9d3ba0";
var CHORD_DISABLED_COLOR = "#aaaaaa";
var CHORD_BLINK_COLOR = "#eeeeee";
var chords;
var connected = false;
function start() {
    chords = document.getElementsByTagName("span");
    for (var i = 0; i < chords.length; i++) {
        chords[i].onclick = chordClick;
    }
    ping();
}
function settings() {
    stat();
}
function stat() {
    return __awaiter(this, void 0, void 0, function () {
        var system_elem, status, c;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    console.log("Getting system status ...");
                    system_elem = document.getElementById("system");
                    if (!system_elem) {
                        return [2 /*return*/];
                    }
                    system_elem.innerHTML = "Checking device   .";
                    status = null;
                    fetch("/device/diag")
                        .then(function (response) { return response.text(); })
                        .then(function (data) { return (status = JSON.parse(data)); }) // Parse to remove quotes
                    ["catch"](function (ex) {
                        status = "error";
                        console.log("status = %s", status);
                    });
                    c = 0;
                    _a.label = 1;
                case 1:
                    if (!!status) return [3 /*break*/, 3];
                    console.log("status = %s", status);
                    system_elem.innerHTML =
                        c % 2 ? "Checking device . ." : "Checking device ...";
                    return [4 /*yield*/, new Promise(function (r) { return setTimeout(r, 1000); })];
                case 2:
                    _a.sent();
                    c++;
                    return [3 /*break*/, 1];
                case 3:
                    console.log("status = %s", status);
                    system_elem.innerHTML = status;
                    return [2 /*return*/];
            }
        });
    });
}
function chordClick() {
    if (connected === false) {
        return;
    }
    hideAlerts();
    // Toggle clicked chord color
    if (this.getAttribute("status") == "clicked") {
        this.setAttribute("status", "");
        this.style.backgroundColor = CHORD_COLOR;
        setChord(0);
    }
    else {
        this.setAttribute("status", "clicked");
        this.style.backgroundColor = CHORD_ACTIVE_COLOR;
        setChord(this.id);
    }
    // Reset rest of the chord colors
    for (var i = 0; i < chords.length; i++) {
        if (chords[i].id != this.id) {
            chords[i].style.backgroundColor = CHORD_COLOR;
            chords[i].setAttribute("status", "");
        }
    }
}
function hideAlerts() {
    var alert_elem = document.getElementById("header");
    if (alert_elem) {
        alert_elem.style.display = "none";
    }
}
function delay(time) {
    return new Promise(function (resolve) { return setTimeout(resolve, time); });
}
function setChordColors(color) {
    for (var i = 0; i < chords.length; i++) {
        chords[i].style.backgroundColor = color;
    }
}
function ping() {
    return __awaiter(this, void 0, void 0, function () {
        var alert_elem, pong, c, i;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    console.log("ping ...");
                    alert_elem = document.getElementById("header");
                    if (!alert_elem) {
                        return [2 /*return*/];
                    }
                    alert_elem.textContent = "Connecting ...";
                    pong = null;
                    fetch("/device/ping")
                        .then(function (response) {
                        pong = response.status;
                    })["catch"](function (ex) {
                        pong = "error";
                        console.log("ping = %s", pong);
                    });
                    c = 0;
                    _a.label = 1;
                case 1:
                    if (!!pong) return [3 /*break*/, 3];
                    console.log("ping = %s", pong);
                    for (i = 0; i < chords.length; i++) {
                        setChordColors(c % 2 ? CHORD_BLINK_COLOR : CHORD_DISABLED_COLOR);
                    }
                    return [4 /*yield*/, new Promise(function (r) { return setTimeout(r, 1000); })];
                case 2:
                    _a.sent();
                    c++;
                    return [3 /*break*/, 1];
                case 3:
                    console.log("ping = %s", pong);
                    setChordColors(CHORD_DISABLED_COLOR);
                    if (pong == 200) {
                        connected = true;
                        alert_elem.textContent = "Touch chords to play";
                        setChordColors(CHORD_COLOR);
                    }
                    else {
                        alert_elem.innerHTML =
                            "Check connection and <a href='index.html'>retry</a>";
                    }
                    return [2 /*return*/];
            }
        });
    });
}
function setChord(chord) {
    return __awaiter(this, void 0, void 0, function () {
        var response, data;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, fetch("/chord/" + chord)];
                case 1:
                    response = _a.sent();
                    return [4 /*yield*/, response.json()];
                case 2:
                    data = _a.sent();
                    console.log("chord set %s = %s", chord, data);
                    return [2 /*return*/];
            }
        });
    });
}
