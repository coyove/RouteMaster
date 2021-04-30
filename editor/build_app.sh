#!/bin/sh

python3 setup.py py2app

TOP=$(pwd)

cd ./dist/RouteMaster.app/Contents/Resources/lib/python3.9/PyQt5/Qt5/plugins
rm -rf assetimporters gamepads geoservices mediaservice playlistformats sensorgestures audio position sensors texttospeech bearer geometryloaders platformthemes printsupport sceneparsers sqldrivers webview

cd ../qml
rm -rf *

z__clean() {
    rm -rf QtQuick* QtQml* QtSql* QtSensor* QtNfc* \
    QtSerialPort* QtBluetooth* QtMultimedia* QtOpenGL* \
    QtTextToSpeech* QtWeb* QtPositioning* QtXml* \
    QtDesigner* QtTest* QtLocation* QtHelp*
}

cd ../lib
z__clean

cd ../../
z__clean

cd $TOP/dist/RouteMaster.app
du -sh .

cd $TOP
cp logo.png ./dist/RouteMaster.app/Contents/Resources/PythonApplet.icns