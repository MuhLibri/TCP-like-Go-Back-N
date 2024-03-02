import argparse

class Parser:
    def __init__(self, is_client: bool = False):
        self.broadcast_port = "" 
        self.client_port = ""
        self.pathfile_input = ""
        self.pathfile_output = ""
        self.is_client = is_client
        
        if is_client:
            parser = argparse.ArgumentParser(
                description="Client handling file from server"
            )
            parser.add_argument(
                "client_port",
                metavar="[client port]",
                type=int,
                help="client port start the device",
            )
            parser.add_argument(
                "broadcast_port",
                metavar="[broadcast port]",
                type=int,
                help="broadcast port for destination address"
            )
            parser.add_argument(
                "pathfile_output",
                metavar="[path file output]",
                type=str,
                help="output path location"
            )
            args = parser.parse_args()
            self.client_port = getattr(args, "client_port")
            self.broadcast_port = getattr(args, "broadcast_port")
            self.pathfile_output = getattr(args, "pathfile_output")
        else:
            parser = argparse.ArgumentParser(
                description="Server handling file to client"
            )
            parser.add_argument(
                "broadcast_port",
                metavar="[broadcast port]",
                type=int,
                help="Broadcast port for client",
            )
            parser.add_argument(
                "pathfile_input",
                metavar="[path file input]",
                type=str,
                help="Path file want to send"
            )
            args = parser.parse_args()
            self.port = getattr(args, "broadcast_port")
            self.pathfile_input = getattr(args, "pathfile_input")

    def get_values(self):
        if self.is_client:
            return self.client_port, self.broadcast_port, self.pathfile_output
        else:
            return self.port, self.pathfile_input
        
    def __str__(self):
        if self.is_client:
            return f"Client Parser:\n Client Port: {self.client_port}\n Broadcast port: {self.broadcast_port}\n Output pathfile: {self.pathfile_input}"
        else:
             return f"Server Parser:\n Broadcast port: {self.broadcast_port}\n Input pathfile: {self.pathfile_input}"
                        