# Implementation Protokol TCP-like Go-Back-N

This repository contains how to simulate TCP connection with Automatic Repeat Request (ARQ) algorithm. It consist of simple server and client, server can send file to a or multiple client. 

## Members - binjai

| Name                           |   NIM    |
| ------------------------------ | :------: |
| Muhammad Equilibrie Fajria     | 13521047 |
| Mutawally Nawwar               | 13521065 |
| Ferindya Aulia Berlianty       | 13521161 |

## Usage

server.py

```
usage: server.py [broadcast port] [Path file input]
```

client.py

```
usage: client.py [client port] [broadcast port] [path file output]
```

## Features implemented

1. Checksum 
2. Segment
3. Connection
4. Go Back N when network are unreliable
5. Three way handshake
6. File will be write in `out` directory
7. Tic-tac-toe

## How to use

1. Run server by inserting the broadcast port and source file instructions in [Usage](#usage)

   example:
   `python server.py 8000 ./in/gambar.png`
3. If filename aren't exists program will exit
4. Run client by inserting the port, broadcast port and filename see in [Usage](#usage)

   example:
   `python client.py 8001 8000 gambar1.png`
6. File will be write in `out/gambar1.png`
7. Make sure the port are different for `broadcast address` and `client address`

## How to use tic-tac-toe

1. Run server by inserting the broadcast port and source file instructions in [Usage](#usage)

   example:
   `python server.py 8000 ./in/gambar.png`
3. If filename aren't exists program will exit
4. Run two client by inserting the port, broadcast port and tictactoe

   example:
   `python client.py 8001 8000 tictactoe`
   `python client.py 8002 8000 tictactoe`
6. Make sure the port are different for `broadcast address` and `client address`
7. Tic-tac-toe will be started
