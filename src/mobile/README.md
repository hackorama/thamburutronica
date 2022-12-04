# Thamburutronica web app

A mobile web app to control the Thamburatronica device from the phone using the local Wi-Fi network.

![Mobile App](/images/mobile-app.png)

The Pi Pico W microcontroller used on the device comes with Wi-Fi connection and runs a web server.
But we use that web server only for basic HTTP API calls to control the device.
since we do not want the microcontroller to be overloaded serving the web app UI front end resources.

This mobile app service is deployed on a separate server like a Raspberry Pi or Mac mini on the same Wi-Fi network.

## Control flow

### Mac mini web app service

- Mobile app service starts on Mac mini
- Starts serving the web app on local Wi-Fi network

### Thamburutronica device

- Device on start up connects to the pre-configured Wi-Fi SSID access point
  - Starts an HTTP server and listens for device control API calls
  - Connects to the mobile app service on Mac mini and registers the device IP address

### Mobile phone web app UI

- On load the front end UI app checks for registered device connectivity using app service API
- If app service can ping the device the web app UI is loaded and ready to control the device
- And UI chord clicks are proxied/validated and send to the device by mobile app service
- if app service cannot ping the device an error message is shown on the UI to check device status

## Server

```shell
$ ./setup.sh

$ ./server.sh
Server starting ...
Server started 93142 ...

$ tail -f server.log
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
...
INFO:     Application startup complete.
```

```shell
$ curl http://17.0.0.1/health
"OK"
$ curl http://macmini.homelocal.net/health
"OK"
```

Stop the server

```shell
$ kill `cat run.pid`
```

