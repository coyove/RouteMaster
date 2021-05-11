# RouteMaster

<img src="https://raw.githubusercontent.com/coyove/RouteMaster/master/editor/data/logo.png" width="100">

RouteMaster is a simple route designer using [BSicons](https://commons.wikimedia.org/wiki/BSicon).

## Running
1. Download the executable from the [release](https://github.com/coyove/RouteMaster/releases) page

## Running from Source
1. Make sure `Python3.9` and `PyQt5` are installed
2. Run `cd editor && python editor.py`

## Crawling
1. If you are not a developer, you should ignore the following instructions
2. Make sure `golang` is installed
3. Run `go run main.go` to crawl and download BSicons

## Blocks Pack
When first launched, the app will instruct you to unpack blocks (`blcoks.7z`) into a defined directory. To accomplish this step, you should first have `7-zip` or `p7zip` installed.

## Inkscape
For graphically complex blocks, you have to install `inkscape` to let the app render them properly.

## Auto Downloads
If you paste marked text from wikipedia into the app (e.g.: `{{Routemap ...}}`), app will try to parse it and load the corresponding blocks. Any locally missing blocks will be downloaded from wikimedia. If you have difficulties accessing the internet, use flag `--disable-download` to disable the feature.

## UI Basic
- Search and select blocks at top
- Place blocks into canvas by clicking at a desired position, hold Shift to continue placing, hold Ctrl to overlay a block onto an existing one
- Click to select a block, Shift-Click to select multiple blocks, Ctrl-Click to un-select
- Drag selected blocks to new positions
- Shift-Click at a blank spot in canvas to start drawing a free circle which will select all blocks inside
