Esp32cam security camera Server

-------Repo------
This repo is meant to be the server from the esp32cam security camera, the UI is writen in Pyqt5 and its meant to be display on a Rpi3 and a 7 inch screen, if needed it can be used on another screen size, it just need to be adjusted the window resolution

TODO
-- add a way to handle socket error, address already in use
-- find a way to close all sockets properly when the program ends or crash
-- create wifi spot on the Rpi3, so the camera can connect without external wifi router

V0.1
-- created UI for Rpi3 using Pyqt5
-- added extract_jpeg for image analicis
-- added Logfile for error handling